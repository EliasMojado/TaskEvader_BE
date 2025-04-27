from rest_framework import serializers
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
            'id', 'title', 'description', 'deadline', 
            'priority', 'status', 'parent', 'children',
            'collaborators',
        )

    def create(self, validated_data):
        # Extract any collaborators provided
        collaborators = validated_data.pop('collaborators', [])
        # Create the node
        node = Node.objects.create(**validated_data)
        # Set collaborators (and always include the creator)
        node.collaborators.set(collaborators)
        node.collaborators.add(self.context['request'].user.userprofile)
        return node

    def update(self, instance, validated_data):
        # If collaborators are included, replace them
        if 'collaborators' in validated_data:
            instance.collaborators.set(validated_data.pop('collaborators'))
        # Update other fields
        for attr, val in validated_data.items():
            setattr(instance, attr, val)
        instance.save()
        return instance

    def validate_parent(self, parent):
        """
        Optional: ensure the requesting user is a collaborator on the parent node.
        """
        user_profile = self.context['request'].user.userprofile
        if parent and user_profile not in parent.collaborators.all():
            raise serializers.ValidationError(
                "You must be a collaborator on the parent task to nest under it."
            )
        return parent
