from rest_framework import generics, status
from rest_framework.response import Response
from django.utils import timezone
from django.contrib.auth import get_user_model
from ..models import OwnerApplication, Restaurant
from ..serializers import OwnerApplicationSerializer, OwnerApplicationListSerializer, AdminApproveRejectSerializer
from ..permissions import IsAdmin

User = get_user_model()


class AdminOwnerApplicationListView(generics.ListAPIView):
    queryset = OwnerApplication.objects.all().select_related('user', 'reviewed_by')
    serializer_class = OwnerApplicationListSerializer
    permission_classes = [IsAdmin]


class AdminOwnerApplicationDetailView(generics.RetrieveAPIView):
    queryset = OwnerApplication.objects.all().select_related('user', 'reviewed_by')
    serializer_class = OwnerApplicationSerializer
    permission_classes = [IsAdmin]


class AdminApproveView(generics.GenericAPIView):
    queryset = OwnerApplication.objects.all().select_related('user')
    permission_classes = [IsAdmin]
    serializer_class = AdminApproveRejectSerializer

    def patch(self, request, pk):
        app = self.get_object()
        if app.status != 'PENDING':
            return Response(
                {'detail': f'Application is already {app.status}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = AdminApproveRejectSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        review_notes = serializer.validated_data.get('review_notes', '')

        app.status = 'APPROVED'
        app.review_notes = review_notes
        app.reviewed_by = request.user
        app.reviewed_at = timezone.now()
        app.save(update_fields=['status', 'review_notes', 'reviewed_by', 'reviewed_at'])

        user = app.user
        user.role = 'OWNER'
        user.save(update_fields=['role'])

        restaurant = Restaurant.objects.create(
            owner=user,
            name=app.restaurant_name,
            address=app.business_address,
            city=app.city,
            google_maps_link=app.google_maps_link,
            operating_hours=app.operating_hours or '',
            phone=app.contact_phone or '',
        )
        return Response({
            'application': OwnerApplicationSerializer(app).data,
            'restaurant': {'id': restaurant.id, 'name': restaurant.name},
        }, status=status.HTTP_200_OK)


class AdminRejectView(generics.GenericAPIView):
    queryset = OwnerApplication.objects.all()
    permission_classes = [IsAdmin]
    serializer_class = AdminApproveRejectSerializer

    def patch(self, request, pk):
        app = self.get_object()
        if app.status != 'PENDING':
            return Response(
                {'detail': f'Application is already {app.status}.'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        serializer = AdminApproveRejectSerializer(data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        review_notes = serializer.validated_data.get('review_notes', '')

        app.status = 'REJECTED'
        app.review_notes = review_notes
        app.reviewed_by = request.user
        app.reviewed_at = timezone.now()
        app.save(update_fields=['status', 'review_notes', 'reviewed_by', 'reviewed_at'])

        return Response(OwnerApplicationSerializer(app).data, status=status.HTTP_200_OK)
