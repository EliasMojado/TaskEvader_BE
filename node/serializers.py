from rest_framework import serializers
from django.shortcuts import get_object_or_404
from .models import Node
from accounts.models import UserProfile

class NodeSerializer(serializers.ModelSerializer):
    # Show children IDs in responses
    children = serializers.PrimaryKeyRelatedField(
        many=True, read_only=True
    )
    # Allow clients to set collaborators by UserProfile ID
    collaborators = serializers.PrimaryKeyRelatedField(
        many=True, queryset=UserProfile.objects.all(),
        required=False
    )
    # Allow a parent ID (or null)
    parent = serializers.PrimaryKeyRelatedField(
        queryset=Node.objects.all(), allow_null=True, required=False
    )

    class Meta:
        model = Node
        fields = (
            'id', 'title', 'description', 'deadline', 'priority', 'status',
            'parent', 'children', 'collaborators', 'completed_subtasks'
        )

    def get_user_profile(self):
        """
        Helper to fetch the UserProfile for the request user
        """
        request = self.context.get('request')
        return get_object_or_404(UserProfile, username=request.user.username)

    def create(self, validated_data):
        # Extract collaborators list if provided
        collaborators = validated_data.pop('collaborators', [])
        # Create the node
        node = Node.objects.create(**validated_data)
        # Include provided collaborators and always add creator
        profile = self.get_user_profile()
        node.collaborators.set(collaborators)
        node.collaborators.add(profile)
        return node
    
    def update(self, instance, validated_data):
        # Replace collaborators if provided
        if 'collaborators' in validated_data:
            instance.collaborators.set(validated_data.pop('collaborators'))
        # Update other fields
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance
    
    def validate_parent(self, parent):
        """
        Ensure the user is a collaborator on the parent before nesting under it.
        """
        if parent:
            profile = self.get_user_profile()
            if profile not in parent.collaborators.all():
                raise serializers.ValidationError(
                    "You must be a collaborator on the parent task to nest under it."
                )
        return parent
