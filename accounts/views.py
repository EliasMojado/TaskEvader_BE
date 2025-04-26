from rest_framework import generics
from .models      import User
from .serializers import UserSerializer
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User as AuthUser
from rest_framework.permissions import AllowAny

class MyAccountAPIView(generics.RetrieveUpdateAPIView):
    """
    GET  /api/account/    → return your profile
    PUT  /api/account/    → replace your profile
    PATCH /api/account/   → partial update
    """
    serializer_class = UserSerializer

    def get_object(self):
        # DRF already checks TokenAuthentication & IsAuthenticated
        return User.objects.get(username=self.request.user.username)
    

class RegisterAPIView(generics.CreateAPIView):
    """
    POST /api/register/
      - Create a new client User
    """
    serializer_class = UserSerializer
    permission_classes = [AllowAny]   # open to unauthenticated users

    def create(self, request, *args, **kwargs):
        # 1) create the client profile
        resp = super().create(request, *args, **kwargs)
        username = resp.data['username']
        raw_pass = request.data.get('password')

        # 2) create a real auth-User
        auth_user = AuthUser.objects.create_user(
            username=username,
            password=raw_pass
        )

        # 3) create/get its token
        token, _ = Token.objects.get_or_create(user=auth_user)
        resp.data['token'] = token.key

        return resp