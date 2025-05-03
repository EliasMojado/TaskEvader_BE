from django.urls import path
from .views import MyAccountAPIView, RegisterAPIView, ProfileByIdAPIView, CompleteProfileAPIView, ChangePasswordAPIView, \
    UserSearchAPIView, HealthCheckAPIView

urlpatterns = [
    path('account/', MyAccountAPIView.as_view(), name='my-account'),
    path('register/', RegisterAPIView.as_view(), name='register'),
    path('profile/<int:pk>/', ProfileByIdAPIView.as_view(), name='profile-by-id'),
    path('complete-profile/', CompleteProfileAPIView.as_view(), name='complete-profile'),
    path('change-password/', ChangePasswordAPIView.as_view(), name='change-password'),
    path('search-users/', UserSearchAPIView.as_view(), name='search-users'),
    path('health/', HealthCheckAPIView.as_view(), name='health-check'),
]