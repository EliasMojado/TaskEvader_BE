# accounts/views.py

from rest_framework import generics
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models      import UserProfile
from .serializers import RegisterSerializer, UserProfileSerializer, MinimalProfileSerializer, CompleteProfileSerializer, ChangePasswordSerializer
from django.contrib.auth.models import User as AuthUser
from rest_framework.response import Response
from rest_framework import status

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


class ProfileByIdAPIView(generics.RetrieveAPIView):
    """
    GET /api/profile/<id>/ 
      → Returns only display_name and profile_pic for a specific user
    """
    serializer_class = MinimalProfileSerializer
    permission_classes = [IsAuthenticated]
    queryset = UserProfile.objects.all()


class CompleteProfileAPIView(generics.RetrieveAPIView):
    """
    GET /api/complete-profile/
      → Returns username, display_name, profile_pic from UserProfile
      → Also includes first_name, last_name, email from AuthUser
    """
    serializer_class = CompleteProfileSerializer
    permission_classes = [IsAuthenticated]
    
    def get_object(self):
        # Get the UserProfile for the current user
        profile = UserProfile.objects.get(username=self.request.user.username)
        
        # Attach the AuthUser instance to the profile for the serializer to access
        profile.auth_user = AuthUser.objects.get(username=profile.username)
        
        return profile
    

class ChangePasswordAPIView(generics.GenericAPIView):
    """
    POST /api/change-password/
      → Changes user password
      → Requires current_password and new_password
    """
    serializer_class = ChangePasswordSerializer
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # Get the user's AuthUser instance
            auth_user = request.user
            
            # Set the new password
            auth_user.set_password(serializer.validated_data['new_password'])
            auth_user.save()
            
            # Update the UserProfile password as well
            profile = UserProfile.objects.get(username=auth_user.username)
            profile.set_password(serializer.validated_data['new_password'])
            
            return Response({
                "message": "Password changed successfully."
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)