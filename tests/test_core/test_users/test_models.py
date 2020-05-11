from datetime import date
from unittest import mock

import pytest
from django.conf import settings
from freezegun import freeze_time

from dook.api.users.exceptions import UserAlreadyExistException
from dook.core.users.constants import InvitationStatusType
from dook.core.users.models import Invitation
from tests.factories.users import InvitationFactory, UserFactory


class TestInvitationModel:
    @pytest.mark.django_db
    @pytest.mark.parametrize(
        "status, result",
        [
            (InvitationStatusType.USED, True),
            (InvitationStatusType.FAILED, True),
            (InvitationStatusType.WAITING, False),
            (InvitationStatusType.IN_PROGRESS, False),
        ],
    )
    def test_expired_with_status(self, status, result):
        invitation = InvitationFactory(status=status)
        assert invitation.key_expired() is result

    @pytest.mark.django_db
    @freeze_time("2020-04-12")
    @pytest.mark.parametrize(
        "sent_at, result",
        [
            ("2020-04-04", True),
            ("2020-04-05", True),
            ("2020-04-06", False),
            ("2020-04-12", False),
        ],
    )
    def test_expired_with_date(self, sent_at, result):
        invitation = InvitationFactory(sent_at=date.fromisoformat(sent_at))
        assert invitation.key_expired() is result

    @pytest.mark.django_db
    def test_send_invitation(self):
        with mock.patch.multiple(
            "dook.core.users.models", send_registration_invitation_email=mock.DEFAULT
        ) as mocked:
            mocked["send_registration_invitation_email"].return_value = True
            invitation = InvitationFactory()
            invite_url = (
                f"https://{settings.PANEL_DOMAIN_NAME}/register/{invitation.token}"
            )
            invitation.send_invitation(request=["dummy"])

            email_args = {"email": invitation.email, "invite_url": invite_url}

            mocked["send_registration_invitation_email"].assert_called()
            mocked["send_registration_invitation_email"].assert_called_with(**email_args)

    @pytest.mark.django_db
    def test_if_already_exist(self):
        user = UserFactory()
        with pytest.raises(UserAlreadyExistException):
            Invitation.check_if_already_exist(email=user.email)
