from django.db import models
from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.utils.deconstruct import deconstructible
from django.core import validators
import hashlib

@deconstructible
class UnicodeMobileNumberValidator(validators.RegexValidator):
    regex = r"09(\d{9})$"
    message = "username(phone) must be numbers of 11 digits."
    flags = 0


class MyUserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, phone, password, **extra_fields):
        if not phone:
            raise ValueError("enter username please.")
        # email = self.normalize_email(email)
        phone = self.normalize_phone(phone)
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(
        self,
        phone,
        password=None,
        salt=None,
        email=None,
        fname=None,
        lname=None,
        **extra_fields
    ):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(
            phone,
            password,
            email=email,
            salt=salt,
            fname=fname,
            lname=lname,
            **extra_fields
        )

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        if extra_fields.get("is_staff") is not True:
            raise ValueError("Superuser must have is_staff=True.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("Superuser must have is_superuser=True.")
        return self._create_user(phone, password, **extra_fields)

    def normalize_phone(self, phone):
        return phone


class User(AbstractUser):
    phone_validator = UnicodeMobileNumberValidator()

    username = models.CharField(
        "username",
        max_length=150,
        unique=False,
        null=True,
        blank=True,
        help_text="Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only",
    )

    phone = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="phone",
        validators=[phone_validator],
        error_messages={
            "unique": "A user with that mobile number already exists.",
        },
    )

    fullname = models.CharField(
        max_length=50,null=True, blank=True
    )

    salt = models.CharField(max_length=32, null=True, blank=True)

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []
    objects = MyUserManager()

    def get_upload_prefix(self):
        return str(hashlib.md5(str(self.phone).encode()).hexdigest())[0:15]

    def __str__(self) -> str:
        return f"{self.phone}-{self.fullname}" or ""
