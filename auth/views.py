from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    LoginSerializer,
    UserSerializer,
    UserUpdateSerializer
)
from .utils import hash_password, verify_password, create_session, delete_session, delete_all_user_sessions
from .permissions import HasElementPermission


@method_decorator(csrf_exempt, name='dispatch')
class UserRegistrationView(APIView):
    """User registration endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            # Hash password
            password_hash = hash_password(serializer.validated_data['password'])
            
            # Create user
            user = User.objects.create(
                first_name=serializer.validated_data['first_name'],
                last_name=serializer.validated_data['last_name'],
                patronymic=serializer.validated_data.get('patronymic', ''),
                email=serializer.validated_data['email'],
                password_hash=password_hash,
                is_active=True
            )
            
            # Return user data (without password)
            user_serializer = UserSerializer(user)
            return Response(user_serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class LoginView(APIView):
    """User login endpoint"""
    permission_classes = [AllowAny]
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        # Find user
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Check if user is active
        if not user.is_active:
            return Response({'error': 'Account is deactivated'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Verify password
        if not verify_password(password, user.password_hash):
            return Response({'error': 'Invalid email or password'}, status=status.HTTP_401_UNAUTHORIZED)
        
        # Create session
        session = create_session(user)
        
        # Return user data with session cookie
        user_serializer = UserSerializer(user)
        response = Response(user_serializer.data, status=status.HTTP_200_OK)
        
        # Set session cookie
        response.set_cookie(
            'sessionid',
            str(session.session_id),
            max_age=settings.SESSION_EXPIRE_SECONDS,
            httponly=True,
            secure=settings.SESSION_COOKIE_SECURE,
            samesite=settings.SESSION_COOKIE_SAMESITE
        )
        
        return response


@method_decorator(csrf_exempt, name='dispatch')
class LogoutView(APIView):
    """User logout endpoint"""
    
    def post(self, request):
        session_id = request.COOKIES.get('sessionid')
        
        if session_id:
            delete_session(session_id)
        
        response = Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
        response.delete_cookie('sessionid')
        return response


@method_decorator(csrf_exempt, name='dispatch')
class ProfileView(APIView):
    """User profile view and update endpoint"""
    
    def get(self, request):
        """Get current user profile"""
        if not request.user or not hasattr(request.user, 'id'):
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = UserSerializer(request.user)
        return Response(serializer.data)
    
    def patch(self, request):
        """Update current user profile"""
        if not request.user or not hasattr(request.user, 'id'):
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = UserUpdateSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            user_serializer = UserSerializer(request.user)
            return Response(user_serializer.data)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@method_decorator(csrf_exempt, name='dispatch')
class DeleteAccountView(APIView):
    """Delete user account (soft delete)"""
    
    def delete(self, request):
        if not request.user or not hasattr(request.user, 'id'):
            return Response({'error': 'Authentication required'}, status=status.HTTP_401_UNAUTHORIZED)
        
        user = request.user
        
        # Soft delete: set is_active=False
        user.is_active = False
        user.save()
        
        # Delete all user sessions
        delete_all_user_sessions(user)
        
        # Logout: clear session cookie
        response = Response({'message': 'Account deleted successfully'}, status=status.HTTP_200_OK)
        response.delete_cookie('sessionid')
        
        return response
