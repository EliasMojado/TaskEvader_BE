from rest_framework import serializers
from .models import UserProfile
from django.contrib.auth.models import User as AuthUser
from rest_framework.authtoken.models import Token

class UserProfileSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = UserProfile
        fields = ('username', 'display_name', 'profile_pic', 'password',)

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
    
class RegisterSerializer(serializers.ModelSerializer):
    # Profile fields
    display_name = serializers.CharField(required=True, allow_blank=False)

    # AuthUser fields — write_only so they don't get read from UserProfile
    first_name = serializers.CharField(write_only=True, required=True, allow_blank=False)
    last_name  = serializers.CharField(write_only=True, required=True, allow_blank=False)
    email      = serializers.EmailField   (write_only=True, required=True)
    password   = serializers.CharField    (write_only=True, required=True, allow_blank=False)

    class Meta:
        model  = UserProfile
        fields = (
            'username',
            'password',
            'display_name',
            'profile_pic',
            'first_name',
            'last_name',
            'email',
        )

    def create(self, validated_data):
        # Pop off AuthUser fields
        raw_pass   = validated_data.pop('password')
        first_name = validated_data.pop('first_name')
        last_name  = validated_data.pop('last_name')
        email      = validated_data.pop('email')

        # 1) Create the profile
        profile = super().create(validated_data)
        profile.set_password(raw_pass)

        # 2) Create the AuthUser
        auth_user = AuthUser.objects.create_user(
            username   = profile.username,
            password   = raw_pass,
            first_name = first_name,
            last_name  = last_name,
            email      = email,
        )

        # 3) Issue a token
        Token.objects.create(user=auth_user)

        return profile
