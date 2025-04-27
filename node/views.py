from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Node
from .serializers import NodeSerializer
from accounts.models import UserProfile

def get_user_profile(request):
    """
    Helper to return the UserProfile for the logged-in AuthUser.
    """
    return get_object_or_404(UserProfile, username=request.user.username)

class NodeListCreateAPIView(generics.ListCreateAPIView):
    """
    GET  /api/nodes/        → list all nodes the user collaborates on
    POST /api/nodes/        → create a new node
    """
    serializer_class   = NodeSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        profile = get_user_profile(self.request)
        return Node.objects.filter(collaborators=profile)

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
        profile = get_user_profile(self.request)
        return get_object_or_404(
            Node,
            id=self.kwargs['pk'],
            collaborators=profile
        )
    
class RootNodeListAPIView(APIView):
    """
    GET /api/nodes/roots/
      → list all top-level (parent=None) nodes the user collaborates on
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        profile = get_user_profile(request)
        roots = Node.objects.get_root_nodes(request.user)
        serializer = NodeSerializer(roots, many=True)
        return Response(serializer.data)

class NodeChildrenAPIView(APIView):
    """
    GET /api/nodes/<id>/children/?filter_by_user=true|false
      → list ALL nested descendants of node <id>
         if filter_by_user=true, only those where the user is a collaborator
    """
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        profile = get_user_profile(request)
        node = get_object_or_404(
            Node,
            id=pk,
            collaborators=profile
        )

        # parse the flag (defaults to False)
        fv = request.query_params.get('filter_by_user', 'false').lower()
        filter_by_user = fv in ('1', 'true', 'yes')

        # collect descendants
        children = node.get_all_child_nodes(
            filter_by_user=filter_by_user,
            user=request.user if filter_by_user else None
        )

        serializer = NodeSerializer(children, many=True)
        return Response(serializer.data)