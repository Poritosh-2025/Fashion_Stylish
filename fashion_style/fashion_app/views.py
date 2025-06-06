from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import User, OTP
from .serializers import *
from .utils import send_otp_email
from rest_framework.permissions import AllowAny  # Change this based on your security needs
from django.contrib.auth import get_user_model
User = get_user_model()

class UserRegistrationView(generics.CreateAPIView):
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            'message': 'Registration successful. Please check your email for OTP verification.',
            'email': user.email
        }, status=status.HTTP_201_CREATED)

class OTPVerificationView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = OTPVerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        otp_instance = serializer.validated_data['otp_instance']
        email = serializer.validated_data['email']
        otp_type = serializer.validated_data['otp_type']
        
        # Mark OTP as used
        otp_instance.is_used = True
        otp_instance.save()
        
        if otp_type == 'registration':
            # Activate user
            user = User.objects.get(email=email)
            user.is_active = True
            user.is_verified = True
            user.save()
            
            # Generate JWT tokens
            refresh = RefreshToken.for_user(user)
            return Response({
                'message': 'Email verified successfully. Registration completed.',
                'access_token': str(refresh.access_token),
                'refresh_token': str(refresh),
                'user': UserProfileSerializer(user).data
            }, status=status.HTTP_200_OK)
        
        return Response({
            'message': 'OTP verified successfully.'
        }, status=status.HTTP_200_OK)

class ResendOTPView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = ResendOTPSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        otp_type = serializer.validated_data['otp_type']
        
        # Invalidate old OTPs
        OTP.objects.filter(email=email, otp_type=otp_type, is_used=False).update(is_used=True)
        
        # Create new OTP
        otp = OTP.objects.create(email=email, otp_type=otp_type)
        send_otp_email(email, otp.otp_code)
        
        return Response({
            'message': 'New OTP sent to your email.'
        }, status=status.HTTP_200_OK)

class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        user = serializer.validated_data['user']
        user.last_active = timezone.now()
        user.save()
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'message': 'Login successful.',
            'access_token': str(refresh.access_token),
            'refresh_token': str(refresh),
            'user': UserProfileSerializer(user).data
        }, status=status.HTTP_200_OK)

class UserProfileView(generics.RetrieveAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class UserProfileUpdateView(generics.UpdateAPIView):
    serializer_class = UserProfileUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            'message': 'Profile updated successfully.',
            'user': UserProfileSerializer(self.get_object()).data
        }, status=status.HTTP_200_OK)

class PasswordResetRequestView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        # Invalidate old password reset OTPs
        OTP.objects.filter(email=email, otp_type='password_reset', is_used=False).update(is_used=True)
        
        # Create new OTP
        otp = OTP.objects.create(email=email, otp_type='password_reset')
        send_otp_email(email, otp.otp_code)
        
        return Response({
            'message': 'Password reset OTP sent to your email.'
        }, status=status.HTTP_200_OK)

class PasswordResetView(APIView):
    permission_classes = [permissions.AllowAny]
    
    def post(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        new_password = serializer.validated_data['new_password']
        otp_instance = serializer.validated_data['otp_instance']
        
        # Mark OTP as used
        otp_instance.is_used = True
        otp_instance.save()
        
        # Update user password
        user = User.objects.get(email=email)
        user.set_password(new_password)
        user.save()
        
        return Response({
            'message': 'Password reset successful. You can now login with your new password.'
        }, status=status.HTTP_200_OK)

# Admin Views
class DashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get(self, request):
        if request.user.role not in ['admin', 'superadmin']:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        
        today = timezone.now().date()
        total_users = User.objects.filter(role='user').count()
        new_users = User.objects.filter(role='user', date_created__date=today).count()
        anonymous_users = User.objects.filter(is_anonymous=True).count()
        
        data = {
            'total_users': total_users,
            'new_users': new_users,
            'anonymous_users': anonymous_users
        }
        
        serializer = DashboardSerializer(data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class UserManagementView(generics.ListAPIView):
    serializer_class = UserManagementSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role not in ['admin', 'superadmin']:
            return User.objects.none()
        return User.objects.filter(role='user')

class UserActionView(APIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, user_id):
        if request.user.role not in ['admin', 'superadmin']:
            return Response({'error': 'Permission denied.'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            user = User.objects.get(id=user_id, role='user')
        except User.DoesNotExist:
            return Response({'error': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)
        
        action = request.data.get('action')
        
        if action == 'disable':
            user.is_disabled = True
            user.save()
            return Response({'message': 'User access disabled.'}, status=status.HTTP_200_OK)
        elif action == 'delete':
            user.delete()
            return Response({'message': 'User account deleted.'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Invalid action.'}, status=status.HTTP_400_BAD_REQUEST)

class AdministratorsView(generics.ListAPIView):
    serializer_class = AdminSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role not in ['admin', 'superadmin']:
            return User.objects.none()
        return User.objects.filter(role__in=['admin', 'superadmin'])

class AdminCreateView(generics.CreateAPIView):
    serializer_class = AdminCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def post(self, request, *args, **kwargs):
        if request.user.role != 'superadmin':
            return Response({'error': 'Only Super Admin can create administrators.'}, 
                          status=status.HTTP_403_FORBIDDEN)
        
        response = super().create(request, *args, **kwargs)
        return Response({
            'message': 'Administrator created successfully.',
            'admin': response.data
        }, status=status.HTTP_201_CREATED)

class AdminUpdateView(generics.UpdateAPIView):
    serializer_class = AdminCreateUpdateSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role not in ['admin', 'superadmin']:
            return User.objects.none()
        return User.objects.filter(role__in=['admin', 'superadmin'])
    
    def update(self, request, *args, **kwargs):
        response = super().update(request, *args, **kwargs)
        return Response({
            'message': 'Administrator updated successfully.',
            'admin': response.data
        }, status=status.HTTP_200_OK)

class AdminDeleteView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        if self.request.user.role not in ['admin', 'superadmin']:
            return User.objects.none()
        return User.objects.filter(role__in=['admin', 'superadmin'])
    
    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        return Response({
            'message': 'Administrator account deleted successfully.'
        }, status=status.HTTP_200_OK)
    
class CreateSuperuserView(APIView):
    permission_classes = [AllowAny]  # Be careful with this in production
    
    def post(self, request):
        # Extract data from request
        email = request.data.get('email')
        phone_number = request.data.get('phone_number')
        password = request.data.get('password')
        first_name = request.data.get('first_name', '')
        last_name = request.data.get('last_name', '')
        
        # Validation
        if not email or not phone_number or not password:
            return Response({
                'error': 'Email, phone_number, and password are required.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            return Response({
                'error': 'User with this email already exists.'
            }, status=status.HTTP_400_BAD_REQUEST)
            
        if User.objects.filter(phone_number=phone_number).exists():
            return Response({
                'error': 'User with this phone number already exists.'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            # Create superuser
            user = User.objects.create_user(
                email=email,
                phone_number=phone_number,
                password=password,
                first_name=first_name,
                last_name=last_name,
                role='superadmin',
                is_verified=True,
                is_active=True,
                is_staff=True,
                is_superuser=True
            )
            
            return Response({
                'message': 'Superuser created successfully!',
                'user': {
                    'id': user.id,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'full_name': user.full_name,
                    'role': user.role,
                    'is_verified': user.is_verified,
                    'is_active': user.is_active
                }
            }, status=status.HTTP_201_CREATED)
            
        except Exception as e:
            return Response({
                'error': f'Error creating superuser: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)