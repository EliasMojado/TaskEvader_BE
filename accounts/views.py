# accounts/views.py

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models      import UserProfile
from .serializers import RegisterSerializer, UserProfileSerializer

class RegisterAPIView(generics.CreateAPIView):
    """
    POST /api/register/ 
      → Validates: username, password, display_name, first_name, last_name, email
      → Creates UserProfile + AuthUser + Token
    """
    serializer_class   = RegisterSerializer
    permission_classes = [AllowAny]


class MyAccountAPIView(generics.RetrieveUpdateAPIView):
    """
    GET/PUT/PATCH /api/account/ 
      → Uses UserProfileSerializer; only requires auth_user → fetches matching profile
    """
    serializer_class   = UserProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        return UserProfile.objects.get(username=self.request.user.username)
