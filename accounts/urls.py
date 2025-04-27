from django.urls import path
from .views import MyAccountAPIView, RegisterAPIView, ProfileByIdAPIView
from rest_framework.authtoken.views import obtain_auth_token

urlpatterns = [
    path('account/', MyAccountAPIView.as_view(), name='my-account'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('token-auth/', obtain_auth_token, name='api_token_auth'),
    path('profile/<int:pk>/', ProfileByIdAPIView.as_view(), name='profile-by-id'),
]