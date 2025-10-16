from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.views import APIView
from django.contrib.auth.models import User

from .serializers import UserProfileSerializer, RegistrationSerializer

class UserProfileList(generics.ListAPIView):
    queryset = User.objects.all()
    serializer_class = UserProfileSerializer

class UserProfileDetail():
    pass

class RegistrationView(APIView):
    # Allow any user (authenticated or not) to access this url

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        data = {}

        if serializer.is_valid():
            saved_account = serializer.save()
            # add auth token generation later
            data = {
                # 'token': '', # Token generation logic to be added
                'fullname': saved_account.username,
                'email': saved_account.email,
                'user_id': saved_account.id,
            }
            return Response(data, status=status.HTTP_201_CREATED)
        
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)