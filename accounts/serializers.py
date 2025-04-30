from rest_framework import serializers
from .models import UserProfile
from django.contrib.auth.models import User as AuthUser
from rest_framework.validators import UniqueValidator
from rest_framework.authtoken.models import Token

class UserProfileSerializer(serializers.ModelSerializer):
    # write-only raw password
    password = serializers.CharField(write_only=True, required=False)

    # proxy AuthUser.email here
    email = serializers.EmailField(
        source='auth_user.email',
        required=False,
        validators=[
            UniqueValidator(
                queryset=AuthUser.objects.all(),
                message="This email is already in use."
            )
        ]
    )

    class Meta:
        model = UserProfile
        fields = (
            'username',
            'email',
            'display_name',
            'profile_pic',
            'password',
        )
        read_only_fields = ('username',)  # you probably don’t want to change username here

    def update(self, instance, validated_data):
        # 1) Pop out nested auth_user data
        auth_data = validated_data.pop('auth_user', {})
        raw_password = validated_data.pop('password', None)

        # 2) Update profile fields
        profile = super().update(instance, validated_data)

        # 3) Update the linked AuthUser’s email, if provided
        if 'email' in auth_data:
            auth_user = AuthUser.objects.get(username=instance.username)
            auth_user.email = auth_data['email']
            auth_user.save(update_fields=['email'])

        # 4) Update password, if provided
        if raw_password:
            profile.set_password(raw_password)

        return profile
    
class RegisterSerializer(serializers.ModelSerializer):
    # Profile fields
    display_name = serializers.CharField(required=True, allow_blank=False)

    # AuthUser fields — write_only so they don't get read from UserProfile
    first_name = serializers.CharField(write_only=True, required=True, allow_blank=False)
    last_name  = serializers.CharField(write_only=True, required=True, allow_blank=False)

    email = serializers.EmailField(
        write_only=True,
        required=True,
        validators=[
            UniqueValidator(
                queryset=AuthUser.objects.all(),
                message="A user with that email already exists."
            )
        ]
    )

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

class MinimalProfileSerializer(serializers.ModelSerializer):
    """
    Serializer that only returns display_name and profile_pic
    """
    class Meta:
        model = UserProfile
        fields = ('display_name', 'profile_pic')

class CompleteProfileSerializer(serializers.ModelSerializer):
    # Include the AuthUser fields
    first_name = serializers.CharField(source='auth_user.first_name', read_only=True)
    last_name = serializers.CharField(source='auth_user.last_name', read_only=True)
    email = serializers.EmailField(source='auth_user.email', read_only=True)
    
    class Meta:
        model = UserProfile
        fields = (
            'id',
            'username',
            'display_name',
            'profile_pic',
            'first_name',
            'last_name',
            'email',
        )


class ChangePasswordSerializer(serializers.Serializer):
    current_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, min_length=8)
    
    def validate_current_password(self, value):
        user = self.context['request'].user
        # Check if the current password is correct
        if not user.check_password(value):
            raise serializers.ValidationError("Current password is incorrect.")
        return value