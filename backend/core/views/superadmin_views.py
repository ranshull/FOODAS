from rest_framework import generics
from django.db.models import Q
from django.contrib.auth import get_user_model
from ..models import Role
from ..serializers import (
    SuperAdminUserListSerializer,
    SuperAdminUserCreateSerializer,
    SuperAdminUserUpdateSerializer,
)
from ..permissions import IsSuperAdmin

User = get_user_model()


class SuperAdminUserListView(generics.ListAPIView):
    """List users with optional search by name or email."""
    serializer_class = SuperAdminUserListSerializer
    permission_classes = [IsSuperAdmin]

    def get_queryset(self):
        qs = User.objects.all().order_by('-created_at')
        search = self.request.query_params.get('search', '').strip()
        if search:
            qs = qs.filter(
                Q(name__icontains=search) | Q(email__icontains=search)
            )
        return qs


class SuperAdminUserDetailView(generics.RetrieveUpdateAPIView):
    """Retrieve or update user (role, is_active, etc.)."""
    queryset = User.objects.all()
    serializer_class = SuperAdminUserUpdateSerializer
    permission_classes = [IsSuperAdmin]


class SuperAdminUserCreateView(generics.CreateAPIView):
    """Create user (e.g. new Admin or Auditor)."""
    queryset = User.objects.all()
    serializer_class = SuperAdminUserCreateSerializer
    permission_classes = [IsSuperAdmin]
