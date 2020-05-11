from datetime import datetime

from anymail.exceptions import AnymailAPIError
from django.db import transaction
from django.http import Http404
from django.shortcuts import get_object_or_404
from rest_framework import generics, permissions, status
from rest_framework.authentication import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.authtoken.views import ObtainAuthToken
from rest_framework.response import Response
from rest_framework.settings import api_settings

from dook.api.users.exceptions import (
    EmailNotVerifiedException,
    InternalEmailErrorException,
    InternalSignUpErrorException,
    InvalidCredentialsException,
    InvalidInviteTokenException,
    InvalidPasswordException,
    TokenAlreadyUsedException,
)
from dook.api.users.serializers import (
    AuthTokenSerializer,
    InternalPasswordResetSerializer,
    PasswordResetRequestSerializer,
    PasswordResetSerializer,
    RegistrationInvitationSerializer,
    RegistrationSerializer,
)
from dook.core.users.constants import InvitationStatusType
from dook.core.users.email_service import (
    send_password_reset_email,
    send_registration_confirmation_email,
)
from dook.core.users.models import Invitation, User
from dook.core.users.tokens import get_user_from_uid, password_reset_token_generator


class SignUpView(generics.CreateAPIView):
    permission_classes = (permissions.AllowAny,)
    serializer_class = RegistrationSerializer

    def create(self, request, token=None, *args, **kwargs):
        self.check_if_token_is_valid(token)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        invitation = Invitation.objects.filter(token=token).first()
        serializer.validated_data["role"] = invitation.user_role
        serializer.validated_data["email"] = invitation.email

        self.perform_create(serializer)

        user = serializer.instance
        if not user:
            raise InternalSignUpErrorException
        else:
            self.mark_invitation_as_used(invitation)
            send_registration_confirmation_email(name=user.name, email=user.email)

        serializer.validated_data.pop("password")
        serializer.validated_data.pop("password2")

        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

    def get(self, request, token=None):
        self.check_if_token_is_valid(token)
        invitation = Invitation.objects.filter(token=token).first()
        data = {"email": invitation.email}
        return Response(data, status=status.HTTP_200_OK)

    def check_if_token_is_valid(self, token):
        if token is None:
            raise InvalidInviteTokenException
        try:
            invitation = get_object_or_404(Invitation, token=token)
        except Http404:
            raise InvalidInviteTokenException
        else:
            if invitation.status == InvitationStatusType.USED:
                raise TokenAlreadyUsedException

    def mark_invitation_as_used(self, invitation):
        invitation.status = InvitationStatusType.USED
        invitation.save()
        return True


class CreateTokenView(ObtainAuthToken):
    """ Create a new auth token for user  """

    serializer_class = AuthTokenSerializer
    renderer_classes = api_settings.DEFAULT_RENDERER_CLASSES
    permission_classes = (permissions.AllowAny,)

    def post(self, request, *args, **kwargs):
        serializer = self.serializer_class(
            data=request.data, context={"request": request}
        )
        serializer.is_valid(raise_exception=True)
        user = self.get_user_if_valid(serializer.validated_data)
        token, created = Token.objects.get_or_create(user=user)
        return Response({"token": token.key})

    def get_user_if_valid(self, data):
        email = data["email"].lower()
        password = data["password"]
        user = authenticate(email=email, password=password)

        if not user:
            raise InvalidCredentialsException
        elif user.is_verified is False:
            raise EmailNotVerifiedException
        else:
            return user


class CreateInvitationView(generics.CreateAPIView):
    permission_classes = (permissions.IsAdminUser,)
    serializer_class = RegistrationInvitationSerializer

    @transaction.atomic
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        self.perform_create(serializer)

        invitation = serializer.instance
        self.send_invitation(request, invitation)

        return Response(serializer.validated_data, status=status.HTTP_201_CREATED)

    def send_invitation(self, request, invitation):
        try:
            email_send = invitation.send_invitation(request)
        except AnymailAPIError:
            raise InternalEmailErrorException
        else:
            if email_send is True:
                invitation.sent_at = datetime.utcnow().date()
                invitation.save()
            else:
                raise InternalEmailErrorException


class UserDetailView(generics.RetrieveAPIView):
    permission_classes = (permissions.IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        user = request.user
        data = {"email": user.email, "name": user.name, "role": user.role}
        return Response(data, status=status.HTTP_200_OK)


class PasswordResetRequestView(generics.GenericAPIView):
    permissions = (permissions.AllowAny,)
    serializer_class = PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data["email"]
        if email:
            user = User.objects.filter(email=serializer.validated_data["email"]).first()
            self.send_email(user)

        return Response(
            {"detail": "Check provided email address for further instructions."},
            status=status.HTTP_200_OK,
        )

    def send_email(self, user):
        reset_url = password_reset_token_generator.make_url(user)
        try:
            send_email = send_password_reset_email(email=user.email, reset_url=reset_url)
        except AnymailAPIError:
            raise InternalEmailErrorException
        else:
            if send_email is False:
                raise InternalEmailErrorException


class PasswordResetView(generics.GenericAPIView):
    permissions = (permissions.AllowAny,)
    serializer_class = PasswordResetSerializer

    def get(self, request, uidb64, token):
        password_reset_token_generator.validate_token(uidb64, token)
        return Response("Invalid token.", status=status.HTTP_200_OK)

    def post(self, request, uidb64, token):
        password_reset_token_generator.validate_token(uidb64, token)

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = get_user_from_uid(uidb64)
        self.change_password(user, serializer.validated_data)

        return Response(
            {"detail": "Your password has been reset successfully."},
            status=status.HTTP_200_OK
        )

    def change_password(self, user, data):
        user.set_password(data["password"])
        user.save()


class InternalPasswordResetView(generics.GenericAPIView):
    permissions = (permissions.IsAuthenticated,)
    serializer_class = InternalPasswordResetSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        self.change_password(user, serializer.validated_data)

        return Response(
            {"detail": "Your password has been reset successfully."},
            status=status.HTTP_200_OK
        )

    def change_password(self, user, data):
        if user.check_password(data["old_password"]) is False:
            raise InvalidPasswordException
        else:
            user.set_password(data["password"])
            user.save()
