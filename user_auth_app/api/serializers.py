from django.contrib.auth.models import User

from rest_framework.authtoken.models import Token
from rest_framework import serializers


class UserSerializer(serializers.ModelSerializer):
    """
    Basic user serializer for displaying user information.
    
    Used when showing user data in nested relationships
    (e.g., task assignee, board members).
    
    Note: 'fullname' currently returns username.
    To show actual full names, use user.get_full_name() instead.
    """
    fullname = serializers.CharField(source='username', read_only=True)
    
    class Meta:
        model = User
        fields = ['id', 'email', 'fullname']


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for user profile with authentication token.
    
    Includes the user's authentication token for API access.
    Used in responses after login or profile retrieval.
    
    Fields:
    - token: Authentication token for API requests
    - fullname: User's username (currently)
    - email: User's email address
    - id: User's unique identifier
    """
    fullname = serializers.CharField(source='username', read_only=True)
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['token', 'fullname', 'email', 'id']

    def get_token(self, obj):
        """
        Retrieve or create authentication token for the user.
        
        Returns the token key that should be used in API requests.
        """
        token, created = Token.objects.get_or_create(user=obj)
        return token.key


class RegistrationSerializer(serializers.ModelSerializer):
    """
    Serializer for user registration.
    
    Handles new user account creation with validation for:
    - Fullname (username): Must be unique and not empty
    - Email: Must be unique and valid email format
    - Password: Must be at least 8 characters
    - Password confirmation: Must match password
    
    Note: 'fullname' is mapped to Django's 'username' field.
    
    Returns:
    - Created user account with token
    
    Used for: POST /api/register/
    """
    repeated_password = serializers.CharField(write_only=True)
    email = serializers.EmailField() 
    fullname = serializers.CharField(source='username')

    class Meta:
        model = User
        fields = ['fullname', 'email', 'password', 'repeated_password']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def save(self):
        """
        Create a new user account with validation.
        
        Validates:
        - Fullname is not empty and not already in use
        - Email is not empty and not already in use
        - Password is at least 8 characters
        - Password and repeated_password match
        
        Raises:
        - ValidationError if any validation fails
        
        Returns:
        - Created User instance
        """
        pw = self.validated_data['password']
        pw_repeat = self.validated_data['repeated_password']
        fullname = self.validated_data['username']
        email = self.validated_data.get('email')

        # Validate fullname
        if not fullname or fullname.strip() == '':
            raise serializers.ValidationError({'fullname': 'Fullname is required!'})
        if User.objects.filter(username=fullname).exists():
            raise serializers.ValidationError({'fullname': 'Fullname/Username already in use!'})

        # Validate email
        if not email or email.strip() == '':
            raise serializers.ValidationError({'email': 'Email is required!'})
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Email already in use!'})

        # Validate password
        if not pw or pw.strip() == '':
            raise serializers.ValidationError({'password': 'Password is required!'})
        if len(pw) < 8:
            raise serializers.ValidationError({'password': 'Password must be at least 8 characters long!'})

        # Validate password match
        if pw != pw_repeat:
            raise serializers.ValidationError({'repeated_password': 'Passwords do not match!'})
        
        # Create user account
        account = User(username=self.validated_data['username'], email=self.validated_data['email'])
        account.set_password(pw)  # Hash the password
        account.save()

        return account
    

class LoginSerializer(serializers.Serializer):
    """
    Serializer for user login authentication.
    
    Validates email and password credentials.
    Returns user object if credentials are valid.
    
    Note: Login is email-based, not username-based.
    
    Used for: POST /api/login/
    """
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        """
        Validate login credentials.
        
        Checks:
        - Email is not empty
        - Password is not empty
        - User exists with the given email
        - Password matches the user's hashed password
        
        Raises:
        - ValidationError if credentials are invalid
        
        Returns:
        - data dict with added 'user' key containing User instance
        """
        email = data.get('email')
        password = data.get('password')

        # Validate email field
        if not email or email.strip() == '':
            raise serializers.ValidationError({'email': 'Email is required!'})

        # Validate password field
        if not password or password.strip() == '':
            raise serializers.ValidationError({'password': 'Password is required!'})

        # Check if user exists
        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'error': 'User does not exist!'})

        # Verify password
        if not user.check_password(password):
            raise serializers.ValidationError({'error': 'Invalid credentials!'})

        # Add user to validated data
        data['user'] = user
        return data