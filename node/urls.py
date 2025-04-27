from django.urls import path
from .views import NodeListCreateAPIView, NodeDetailAPIView

urlpatterns = [
    path('nodes/',       NodeListCreateAPIView.as_view(), name='node-list-create'),
    path('nodes/<int:pk>/', NodeDetailAPIView.as_view(), name='node-detail'),
]
