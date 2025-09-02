from django.contrib.auth.models import User
from rest_framework import serializers
from auth_app.models import Profile


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
