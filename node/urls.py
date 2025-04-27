from django.urls import path
from .views import NodeListCreateAPIView, NodeDetailAPIView, RootNodeListAPIView, NodeChildrenAPIView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('nodes/',       NodeListCreateAPIView.as_view(), name='node-list-create'),
    path('nodes/<int:pk>/', NodeDetailAPIView.as_view(), name='node-detail'),
    path('nodes/roots/',            RootNodeListAPIView.as_view(),     name='node-root-list'),
    path('nodes/<int:pk>/children/', NodeChildrenAPIView.as_view(),    name='node-children'),
]

urlpatterns += static(
    settings.MEDIA_URL,
    document_root=settings.MEDIA_ROOT
)