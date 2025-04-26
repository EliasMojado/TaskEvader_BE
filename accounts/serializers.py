from rest_framework import serializers
from .models import User

class UserSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'name', 'profile_pic', 'password',)

    def create(self, validated_data):
        password = validated_data.pop('password')
        user = super().create(validated_data)
        user.set_password(password)
        return user
    
    def update(self, instance, validated_data):
        raw = validated_data.pop('password', None)
        user = super().update(instance, validated_data)
        if raw:
            user.set_password(raw) # hash once, only if provided
        return user
