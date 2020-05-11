from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.authentication import authenticate

from dook.api.users.exceptions import (
    EmailNotVerifiedException,
    InactiveAccountException,
    InvalidCredentialsException,
    PasswordConfirmationFailedException,
)
from dook.core.users.models import Invitation, User
from dook.core.users.validators import validate_password


class RegistrationSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["password", "password2", "name", "specialization"]
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User(
            email=self.validated_data["email"],
            name=self.validated_data["name"],
            specialization=self.validated_data["specialization"],
            role=self.validated_data["role"],
        )
        user.set_password(self.validated_data["password"])
        user.save()
        return user

    def validate(self, data):
        password = data.get("password")
        password2 = data.get("password2")

        if password != password2:
            raise PasswordConfirmationFailedException
        else:
            validate_password(password)
            return data


class AuthTokenSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

    def validate(self, data):
        email = data.get("email").lower()
        password = data.get("password")

        if email and password:
            user = authenticate(email=email, password=password)

            if user:
                if not user.is_active:
                    raise InactiveAccountException
                elif not user.is_verified:
                    raise EmailNotVerifiedException
            else:
                raise InvalidCredentialsException
        else:
            raise InvalidCredentialsException

        data["user"] = user
        return data


class RegistrationInvitationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invitation
        fields = ["email", "user_role"]
        extra_kwargs = {
            "user_role": {
                "required": True,
                "error_messages": {"required": "Field `user_role` is required"},
            },
            "email": {"error_messages": {"required": "Field `email` is required"}},
        }

    def create(self, validated_data):
        invitation = Invitation.create(
            email=self.validated_data["email"],
            user_role=self.validated_data["user_role"],
        )
        return invitation

    def validate(self, data):
        email = data.get("email").lower()
        Invitation.check_if_already_exist(email)

        data["email"] = email
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate(self, data):
        email = data.get("email")
        if User.check_if_user_exist(email=email) is False:
            data["email"] = None

        return data


class PasswordResetSerializer(serializers.Serializer):
    password = serializers.CharField()
    password2 = serializers.CharField()

    def validate(self, data):
        password = data.get("password")
        password2 = data.get("password2")

        if password != password2:
            raise PasswordConfirmationFailedException
        else:
            validate_password(password)
            return data


class InternalPasswordResetSerializer(PasswordResetSerializer):
    old_password = serializers.CharField()
