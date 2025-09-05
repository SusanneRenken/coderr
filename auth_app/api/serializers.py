from django.contrib.auth.models import User
from rest_framework import serializers
from auth_app.models import Profile
from django.utils import timezone


class RegistrationSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)
    repeated_password = serializers.CharField(write_only=True)
    type = serializers.ChoiceField(
        choices=["customer", "business"],
        write_only=True,
        default="customer"
    )

    class Meta:
        model = User
        fields = ["username", "email", "password", "repeated_password", "type"]
        extra_kwargs = {"password": {"write_only": True}}

    def validate(self, attrs):
        if "username" in attrs and attrs["username"] is not None:
            attrs["username"] = attrs["username"].strip()
        if "email" in attrs and attrs["email"] is not None:
            attrs["email"] = attrs["email"].strip().lower()

        if attrs.get("password") != attrs.get("repeated_password"):
            raise serializers.ValidationError(
                {"repeated_password": "Passwords do not match."})

        email = attrs.get("email")
        if email and User.objects.filter(email__iexact=email).exists():
            raise serializers.ValidationError(
                {"email": "Email already exists."})

        return attrs

    def create(self, validated_data):
        validated_data.pop("repeated_password", None)
        user_type = validated_data.pop("type", "customer")

        password = validated_data.pop("password")
        user = User(**validated_data)
        user.set_password(password)
        user.save()

        Profile.objects.create(user=user, type=user_type)

        return user


class ProfileSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)

    first_name = serializers.CharField(
        source='user.first_name', allow_blank=True, required=False)
    last_name = serializers.CharField(
        source='user.last_name', allow_blank=True, required=False)
    email = serializers.EmailField(source='user.email', required=False)

    class Meta:
        model = Profile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type',
            'email',
            'created_at'
        ]
        read_only_fields = ['type', 'created_at']

    def to_representation(self, instance):
        data = super().to_representation(instance)
        return {key: ("" if value is None else value) for key, value in data.items()}
    
    def validate_email(self, value):
        if not value:
            return value
        exists = User.objects.filter(email__iexact=value).exclude(pk=self.instance.user.pk).exists()
        if exists:
            raise serializers.ValidationError("This email is already taken.")
        return value

    def update(self, instance, validated_data):
        if "file" in validated_data:
            file_val = validated_data["file"]
            if file_val in (None, ""):
                if instance.file:
                    instance.file.delete(save=False)
                validated_data["file"] = None
                validated_data["uploaded_at"] = None
            else:
                validated_data["uploaded_at"] = timezone.now() 

        user_data = validated_data.pop("user", {})
        email = user_data.get("email")
        if email is not None:
            user_data["email"] = email.strip().lower()

        for attr in ("first_name", "last_name", "email"):
            if attr in user_data:
                setattr(instance.user, attr, user_data[attr])
        instance.user.save()

        return super().update(instance, validated_data)

class ProfileBusinessSerializer(ProfileSerializer):

    class Meta(ProfileSerializer.Meta):
        model = Profile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'location',
            'tel',
            'description',
            'working_hours',
            'type'
        ]
        read_only_fields = ['type', 'created_at']

class ProfileCustomerSerializer(ProfileSerializer):

    class Meta(ProfileSerializer.Meta):
        model = Profile
        fields = [
            'user',
            'username',
            'first_name',
            'last_name',
            'file',
            'uploaded_at',
            'type'
        ]
