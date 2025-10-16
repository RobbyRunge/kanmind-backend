from django.contrib.auth.models import User

from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.permissions import AllowAny
from rest_framework import serializers

class UserProfileSerializer(serializers.ModelSerializer):
    permission_classes = [AllowAny]
    fullname = serializers.CharField(source='username')
    token = serializers.SerializerMethodField()
    class Meta:
        model = User
        fields = ['token', 'fullname', 'email', 'id']

    def get_token(self, obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key

class UserProfileDetailSerializer(serializers.ModelSerializer):
    permission_classes = [AllowAny]
    fullname = serializers.CharField(source='username')
    token = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['token', 'fullname', 'email', 'id']

    def get_token(self, obj):
        token, created = Token.objects.get_or_create(user=obj)
        return token.key

class RegistrationSerializer(serializers.ModelSerializer):
    permission_classes = [AllowAny]
    repeated_password = serializers.CharField(write_only=True)
    email = serializers.EmailField() 
    fullname = serializers.CharField(
        source = 'username',
    )

    class Meta:
        model = User
        fields = [
            'fullname', 
            'email', 
            'password', 
            'repeated_password']
        extra_kwargs = {
            'password': {
                'write_only': True,
            }
        }

    def save(self):
        pw = self.validated_data['password']
        pw_repeat = self.validated_data['repeated_password']
        fullname = self.validated_data['username']
        email = self.validated_data.get('email')

        if not fullname or fullname.strip() == '':
            raise serializers.ValidationError({'fullname': 'Fullname is required!'})
        if User.objects.filter(username=fullname).exists():
            raise serializers.ValidationError({'fullname': 'Fullname/Username already in use!'})

        if not email or email.strip() == '':
            raise serializers.ValidationError({'email': 'Email is required!'})
        if User.objects.filter(email=email).exists():
            raise serializers.ValidationError({'email': 'Email already in use!'})

        if not pw or pw.strip() == '':
            raise serializers.ValidationError({'password': 'Password is required!'})
        if len(pw) < 8:
            raise serializers.ValidationError({'password': 'Password must be at least 8 characters long!'})

        if pw != pw_repeat:
            raise serializers.ValidationError({'repeated_password': 'Passwords do not match!'})
        
        account = User(username=self.validated_data['username'], email=self.validated_data['email'])
        account.set_password(pw)
        account.save()

        return account
    
class LoginSerializer(serializers.Serializer):
    permission_classes = [AllowAny]
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

    def validate(self, data):
        email = data.get('email')
        password = data.get('password')

        if not email or email.strip() == '':
            raise serializers.ValidationError({'email': 'Email is required!'})

        if not password or password.strip() == '':
            raise serializers.ValidationError({'password': 'Password is required!'})

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            raise serializers.ValidationError({'error': 'User does not exist!'})

        if not user.check_password(password):
            raise serializers.ValidationError({'error': 'Invalid credentials!'})

        data['user'] = user
        return data