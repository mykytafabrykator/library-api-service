from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext as _


class UserManager(BaseUserManager):
    """Define a model manager for User model with no username field."""

    use_in_migrations = True

    def _create_user(
            self,
            email,
            first_name,
            last_name,
            password,
            **extra_fields
    ):
        """Create and save a User with the given email,
        first name, last name, and password."""

        if not email:
            raise ValueError("The given email must be set")

        if not first_name:
            raise ValueError("First name is required")

        if not last_name:
            raise ValueError("Last name is required")

        email = self.normalize_email(email)
        user = self.model(
            email=email,
            first_name=first_name,
            last_name=last_name,
            **extra_fields
        )

        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_user(
            self,
            email,
            first_name,
            last_name,
            password=None,
            **extra_fields
    ):
        """Create and save a regular User with the
        given email, first name, last name, and password."""

        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)

        return self._create_user(
            email,
            first_name,
            last_name,
            password,
            **extra_fields
        )

    def create_superuser(
            self,
            email,
            first_name,
            last_name,
            password,
            **extra_fields
    ):
        """Create and save a SuperUser with the
        given email, first name, last name, and password."""

        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")

        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")

        return self._create_user(
            email,
            first_name,
            last_name,
            password,
            **extra_fields
        )


class User(AbstractUser):
    username = None
    email = models.EmailField(_("email address"), unique=True)
    first_name = models.CharField(_("first name"), max_length=150)
    last_name = models.CharField(_("last name"), max_length=150)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["first_name", "last_name"]

    objects = UserManager()

    class Meta:
        verbose_name = _("User")
        verbose_name_plural = _("Users")
        ordering = ("email",)

    def __str__(self):
        return self.email
