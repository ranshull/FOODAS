from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import OwnerApplication, Restaurant, RestaurantPhoto, Role

User = get_user_model()

# Roles that super admin can assign (cannot create another SUPER_ADMIN via API)
ASSIGNABLE_ROLES = [Role.USER, Role.OWNER, Role.AUDITOR, Role.ADMIN]


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'phone', 'role', 'is_active', 'created_at')
        read_only_fields = ('id', 'role', 'is_active', 'created_at')


class SuperAdminUserListSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'name', 'email', 'phone', 'role', 'is_active', 'created_at')


class SuperAdminUserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('name', 'email', 'phone', 'password', 'role')

    def validate_role(self, value):
        if value not in ASSIGNABLE_ROLES:
            raise serializers.ValidationError('Invalid role for creation.')
        return value

    def create(self, validated_data):
        return User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            phone=validated_data.get('phone', ''),
            password=validated_data['password'],
            role=validated_data['role'],
        )


class SuperAdminUserUpdateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('name', 'email', 'phone', 'role', 'is_active')

    def validate_role(self, value):
        if value not in ASSIGNABLE_ROLES:
            raise serializers.ValidationError('Invalid role.')
        return value


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('name', 'email', 'phone', 'password')

    def create(self, validated_data):
        user = User.objects.create_user(
            email=validated_data['email'],
            name=validated_data['name'],
            phone=validated_data.get('phone', ''),
            password=validated_data['password'],
        )
        return user


class OwnerApplicationSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)
    proof_document_url = serializers.URLField(required=False, allow_blank=True)
    business_card_url = serializers.URLField(required=False, allow_blank=True)
    owner_photo_url = serializers.URLField(required=False, allow_blank=True)
    utility_bill_url = serializers.URLField(required=False, allow_blank=True)
    storefront_photo_url = serializers.URLField(required=False, allow_blank=True)
    dining_photo_url = serializers.URLField(required=False, allow_blank=True)
    google_maps_link = serializers.URLField(allow_blank=False)

    class Meta:
        model = OwnerApplication
        fields = (
            'id', 'user', 'user_email', 'user_name',
            'restaurant_name', 'business_address', 'city', 'google_maps_link', 'landmark',
            'contact_person_name', 'contact_phone', 'alternate_phone', 'operating_hours',
            'proof_document_url', 'business_card_url', 'owner_photo_url', 'utility_bill_url',
            'storefront_photo_url', 'dining_photo_url',
            'declaration_accepted',
            'status', 'review_notes', 'reviewed_by', 'reviewed_at', 'submitted_at',
        )
        read_only_fields = ('id', 'user', 'status', 'review_notes', 'reviewed_by', 'reviewed_at', 'submitted_at')

    def validate(self, data):
        if not data.get('declaration_accepted'):
            raise serializers.ValidationError({'declaration_accepted': 'You must accept the declaration.'})
        proof_fields = [
            data.get('proof_document_url'),
            data.get('business_card_url'),
            data.get('owner_photo_url'),
            data.get('utility_bill_url'),
        ]
        if not any(proof_fields):
            raise serializers.ValidationError(
                'At least one proof document is required (proof document, business card, owner photo, or utility bill).'
            )
        if not data.get('google_maps_link'):
            raise serializers.ValidationError({'google_maps_link': 'Google Maps link is required.'})
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class OwnerApplicationListSerializer(serializers.ModelSerializer):
    user_email = serializers.EmailField(source='user.email', read_only=True)
    user_name = serializers.CharField(source='user.name', read_only=True)

    class Meta:
        model = OwnerApplication
        fields = (
            'id', 'user', 'user_email', 'user_name', 'restaurant_name', 'city',
            'status', 'submitted_at', 'reviewed_at',
        )


class AdminApproveRejectSerializer(serializers.Serializer):
    review_notes = serializers.CharField(required=False, allow_blank=True)


class RestaurantPhotoSerializer(serializers.ModelSerializer):
    class Meta:
        model = RestaurantPhoto
        fields = ('id', 'restaurant', 'image_url', 'caption', 'order')
        read_only_fields = ('id', 'restaurant')


class RestaurantSerializer(serializers.ModelSerializer):
    latitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, allow_null=True, required=False
    )
    longitude = serializers.DecimalField(
        max_digits=9, decimal_places=6, allow_null=True, required=False
    )
    operating_hours = serializers.CharField(required=False, allow_blank=True)
    phone = serializers.CharField(required=False, allow_blank=True)
    google_maps_link = serializers.URLField(required=False, allow_blank=True)

    class Meta:
        model = Restaurant
        fields = (
            'id', 'owner', 'name', 'address', 'city', 'google_maps_link',
            'latitude', 'longitude', 'operating_hours', 'phone', 'status', 'created_at', 'photos'
        )
        read_only_fields = ('id', 'owner', 'status', 'created_at')

    photos = RestaurantPhotoSerializer(many=True, read_only=True)

    def to_internal_value(self, data):
        """Normalize empty strings for decimals to None; preserve URL when blank on partial."""
        data = dict(data) if data is not None else {}
        for key in ('latitude', 'longitude'):
            if key in data and data[key] is not None:
                s = str(data[key]).strip()
                if s == '' or s.lower() == 'null':
                    data[key] = None
                else:
                    try:
                        data[key] = str(float(s))
                    except (TypeError, ValueError):
                        pass
        if self.partial and (data.get('google_maps_link') or '').strip() == '' and self.instance:
            data['google_maps_link'] = (self.instance.google_maps_link or '') or ''
        return super().to_internal_value(data)


class RestaurantPublicSerializer(serializers.ModelSerializer):
    """Public list/detail for browse; no owner."""
    photos = RestaurantPhotoSerializer(many=True, read_only=True)

    class Meta:
        model = Restaurant
        fields = (
            'id', 'name', 'address', 'city', 'google_maps_link',
            'latitude', 'longitude', 'operating_hours', 'phone', 'photos'
        )
