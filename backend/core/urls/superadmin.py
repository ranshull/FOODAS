from django.urls import path
from ..views.superadmin_views import (
    SuperAdminUserListView,
    SuperAdminUserDetailView,
    SuperAdminUserCreateView,
)

urlpatterns = [
    path('users/', SuperAdminUserListView.as_view(), name='superadmin_user_list'),
    path('users/create/', SuperAdminUserCreateView.as_view(), name='superadmin_user_create'),
    path('users/<int:pk>/', SuperAdminUserDetailView.as_view(), name='superadmin_user_detail'),
]
