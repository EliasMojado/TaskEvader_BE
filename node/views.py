from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from .models import Node
from .serializers import NodeSerializer

class NodeListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/nodes/        → list all nodes the user collaborates on
    POST /api/nodes/        → create a new node
    """
    serializer_class   = NodeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        # Only return nodes where the user is a collaborator
        return Node.objects.filter(collaborators=self.request.user.userprofile)

class NodeDetailAPIView(generics.RetrieveUpdateDestroyAPIView):
    """
    GET    /api/nodes/<id>/ → get a single node (if collaborator)
    PUT    /api/nodes/<id>/ → update
    PATCH  /api/nodes/<id>/ → partial update
    DELETE /api/nodes/<id>/ → delete
    """
    serializer_class   = NodeSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Ensures 404 if the user isn’t a collaborator
        return get_object_or_404(
            Node,
            id=self.kwargs['pk'],
            collaborators=self.request.user.userprofile
        )
