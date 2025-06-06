from django.urls import path
from . import views

urlpatterns = [
    # Authentication URLs
    path('register/', views.UserRegistrationView.as_view(), name='user_register'),
    path('verify-otp/', views.OTPVerificationView.as_view(), name='verify_otp'),
    path('resend-otp/', views.ResendOTPView.as_view(), name='resend_otp'),
    path('login/', views.UserLoginView.as_view(), name='user_login'),
    path('register-superadmin/', views.CreateSuperuserView.as_view(), name='superadmin_register'),
    
    # Password Reset URLs
    path('password-reset-request/', views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('password-reset/', views.PasswordResetView.as_view(), name='password_reset'),
    
    # User Profile URLs
    path('profile/', views.UserProfileView.as_view(), name='user_profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='user_profile_update'),
    
    # Admin URLs
    path('admin/dashboard/', views.DashboardView.as_view(), name='admin_dashboard'),
    path('admin/users/', views.UserManagementView.as_view(), name='user_management'),
    path('admin/users/<int:user_id>/action/', views.UserActionView.as_view(), name='user_action'),
    path('admin/administrators/', views.AdministratorsView.as_view(), name='administrators'),
    path('admin/administrators/create/', views.AdminCreateView.as_view(), name='admin_create'),
    path('admin/administrators/<int:pk>/update/', views.AdminUpdateView.as_view(), name='admin_update'),
    path('admin/administrators/<int:pk>/delete/', views.AdminDeleteView.as_view(), name='admin_delete'),
]