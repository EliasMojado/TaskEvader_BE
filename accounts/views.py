# accounts/views.py

from rest_framework import generics, filters
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken

from .models      import UserProfile
from .serializers import RegisterSerializer, UserProfileSerializer, MinimalProfileSerializer, CompleteProfileSerializer, ChangePasswordSerializer
from django.contrib.auth.models import User as AuthUser
from rest_framework.response import Response
from rest_framework import status
from django.db.models import Q

class HealthCheckAPIView(APIView):
    """
    GET /api/health/
      → Returns a simple message to confirm the server is reachable
    """
    permission_classes = [AllowAny]

    def get(self, request, *args, **kwargs):
        return Response({"message": "Server is reachable"}, status=200)

class RegisterAPIView(APIView):
    permission_classes = [AllowAny]
    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if serializer.is_valid():
            profile = serializer.save()

            # Generate tokens for the created user
            auth_user = AuthUser.objects.get(username=profile.username)
            refresh = RefreshToken.for_user(auth_user)

            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            }, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
    

class UserSearchAPIView(generics.ListAPIView):
    """
    GET /api/search-users/?q=<search_term>
      → Searches for users by username or email
      → Excludes the current user from the search results
    """
    serializer_class = CompleteProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        query = self.request.query_params.get('q', '').strip()
        if not query:
            return UserProfile.objects.none()

        # Get the current user
        current_user = self.request.user.username
        
        # Search matching usernames from UserProfile, excluding the current user
        username_matches = UserProfile.objects.filter(username__icontains=query).exclude(username=current_user)

        # Search emails in AuthUser, then get matching usernames, excluding the current user
        email_matches = AuthUser.objects.filter(email__icontains=query).exclude(username=current_user).values_list('username', flat=True)
        email_profile_matches = UserProfile.objects.filter(username__in=email_matches)

        # Combine both querysets using union and exclude the current user
        return (username_matches | email_profile_matches).distinct()



