from django.db import models
from django.utils.translation import gettext_lazy as _


class UserRoleType(models.TextChoices):
    BASE_USER = "base_user", _("Base User")
    FACT_CHECKER = "fact_checker", _("Fact Checker")
    SPECIALIST = "specialist", _("Specialist")
    EXPERT = "expert", _("Expert")
    MODERATOR = "moderator", _("Moderator")
    ADMIN = "admin", _("Admin")


class UserSpecializationType(models.TextChoices):
    JOURNALISM = "journalism", _("Journalism")
    BIOLOGY = "biology", _("Biology")
    PHYSICS = "physics", _("Physics")
    IT = "IT", _("IT")
    CHEMISTRY = "chemistry", _("Chemistry")
    ECONOMY = "economy", _("Economy")
    OTHER = "other", _("Other")


class InvitationStatusType(models.TextChoices):
    FAILED = "failed", _("FAILED")
    WAITING = "waiting", _("WAITING")
    IN_PROGRESS = "in_progress", _("IN_PROGRESS")
    USED = "used", _("USED")


class InvitationUserRoleType(models.TextChoices):
    FACT_CHECKER = "fact_checker", _("Fact Checker")
    SPECIALIST = "specialist", _("Specialist")
    EXPERT = "expert", _("Expert")
    MODERATOR = "moderator", _("Moderator")
