from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.core.validators import URLValidator


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('role', 'SUPER_ADMIN')
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        return self.create_user(email, password, **extra_fields)


class Role(models.TextChoices):
    USER = 'USER', 'User'
    OWNER = 'OWNER', 'Owner'
    AUDITOR = 'AUDITOR', 'Auditor'
    ADMIN = 'ADMIN', 'Admin'
    SUPER_ADMIN = 'SUPER_ADMIN', 'Super Admin'


class User(AbstractUser):
    """Custom user with email as unique identifier and role."""
    username = None
    name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, blank=True)
    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email


class ApplicationStatus(models.TextChoices):
    PENDING = 'PENDING', 'Pending'
    APPROVED = 'APPROVED', 'Approved'
    REJECTED = 'REJECTED', 'Rejected'


class OwnerApplication(models.Model):
    """Stores requests for owner access. Preserved for audit; never deleted."""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owner_applications')

    # Business Information
    restaurant_name = models.CharField(max_length=255)
    business_address = models.TextField()
    city = models.CharField(max_length=100)
    google_maps_link = models.URLField(max_length=500, validators=[URLValidator()])
    landmark = models.CharField(max_length=255, blank=True)

    # Operational Contact
    contact_person_name = models.CharField(max_length=255)
    contact_phone = models.CharField(max_length=20)
    alternate_phone = models.CharField(max_length=20, blank=True)
    operating_hours = models.CharField(max_length=255, blank=True)

    # Proof of Association (at least one required)
    proof_document_url = models.URLField(max_length=500, blank=True)
    business_card_url = models.URLField(max_length=500, blank=True)
    owner_photo_url = models.URLField(max_length=500, blank=True)
    utility_bill_url = models.URLField(max_length=500, blank=True)

    # Restaurant Photos (optional)
    storefront_photo_url = models.URLField(max_length=500, blank=True)
    dining_photo_url = models.URLField(max_length=500, blank=True)

    # Consent
    declaration_accepted = models.BooleanField(default=False)

    # Workflow
    status = models.CharField(
        max_length=20,
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.PENDING
    )
    review_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_applications'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'owner_applications'
        ordering = ['-submitted_at']

    def __str__(self):
        return f'{self.restaurant_name} ({self.status})'

    def has_at_least_one_proof(self):
        return bool(
            self.proof_document_url or
            self.business_card_url or
            self.owner_photo_url or
            self.utility_bill_url
        )


class RestaurantStatus(models.TextChoices):
    ACTIVE = 'ACTIVE', 'Active'
    SUSPENDED = 'SUSPENDED', 'Suspended'


class Restaurant(models.Model):
    """Created only after owner application is approved."""
    owner = models.OneToOneField(User, on_delete=models.CASCADE, related_name='restaurant')
    name = models.CharField(max_length=255)
    address = models.TextField()
    city = models.CharField(max_length=100)
    google_maps_link = models.URLField(max_length=500, validators=[URLValidator()])
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    operating_hours = models.CharField(max_length=255, blank=True)
    phone = models.CharField(max_length=20, blank=True)
    status = models.CharField(
        max_length=20,
        choices=RestaurantStatus.choices,
        default=RestaurantStatus.ACTIVE
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'restaurants'

    def __str__(self):
        return self.name


class RestaurantPhoto(models.Model):
    """Photos for a restaurant: carousel, menu, kitchen, dining, etc. Caption = Storefront, Dining, Kitchen, Menu, Other."""
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE, related_name='photos')
    image_url = models.URLField(max_length=500)
    caption = models.CharField(max_length=100, blank=True)  # e.g. Storefront, Dining, Kitchen, Menu
    order = models.PositiveIntegerField(default=0)

    class Meta:
        db_table = 'restaurant_photos'
        ordering = ['order', 'id']

    def __str__(self):
        return f'{self.restaurant.name} - {self.caption or "Photo"}'
