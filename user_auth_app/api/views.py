from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny
from rest_framework.authtoken.models import Token
from rest_framework.viewsets import ModelViewSet

from .serializers import UserProfileSerializer, RegistrationSerializer, LoginSerializer


class UserProfileListView(ModelViewSet):
    """
    ViewSet for listing all user profiles.
    
    Provides access to all registered users with their profile information.
    Currently set to AllowAny for development - should be restricted in production.
    
    Used for: GET /api/users/ (if configured in URLs)
    """
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer


class UserProfileDetailView(ModelViewSet):
    """
    ViewSet for retrieving individual user profiles.
    
    Provides detailed information about a specific user.
    Currently set to AllowAny for development - should be restricted in production.
    
    Used for: GET /api/users/{id}/ (if configured in URLs)
    """
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer


class RegistrationView(APIView):
    """
    API endpoint for user registration.
    
    Allows new users to create an account with:
    - Fullname (used as username)
    - Email (must be unique)
    - Password (min 8 characters)
    - Password confirmation
    
    On successful registration:
    - Creates new user account
    - Generates authentication token
    - Returns user data with token
    
    POST /api/auth/register/
    Body: {
        "fullname": "John Doe",
        "email": "john@example.com",
        "password": "securepass123",
        "repeated_password": "securepass123"
    }
    
    Returns:
        201: User created successfully with token
        400: Invalid input data or validation errors
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle user registration request.
        
        Creates a new user account and generates an authentication token.
        """
        serializer = RegistrationSerializer(data=request.data)
        data = {}

        if serializer.is_valid():
            # Create user account
            saved_account = serializer.save()
            
            # Generate authentication token
            token = Token.objects.create(user=saved_account)
            
            # Prepare response data
            data = {
                'token': token.key,
                'fullname': saved_account.username,
                'email': saved_account.email,
                'user_id': saved_account.id,
            }
            return Response(data, status=status.HTTP_201_CREATED)
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

class LoginView(APIView):
    """
    API endpoint for user login authentication.
    
    Authenticates users via email and password.
    Uses email-based login instead of username.
    
    On successful login:
    - Validates credentials
    - Retrieves or creates authentication token
    - Returns user data with token
    
    POST /api/auth/login/
    Body: {
        "email": "john@example.com",
        "password": "securepass123"
    }
    
    Returns:
        200: Login successful with token
        400: Invalid credentials or missing fields
    """
    permission_classes = [AllowAny]

    def post(self, request):
        """
        Handle user login request.
        
        Validates credentials and returns authentication token.
        """
        serializer = LoginSerializer(data=request.data)
        data = {}

        if serializer.is_valid():
            # Get authenticated user from validated data
            user = serializer.validated_data['user']
            
            # Get or create authentication token
            token, created = Token.objects.get_or_create(user=user)
            
            # Prepare response data
            data = {
                'token': token.key,
                'fullname': user.username,
                'email': user.email,
                'user_id': user.id,
            }
            return Response(data, status=status.HTTP_200_OK)
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)