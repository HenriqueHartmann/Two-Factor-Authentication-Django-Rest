from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import ugettext_lazy as _

from .managers import CustomUserManager
from .utils import Util

PROFILE = (
    ('normal', 'Normal'),
    ('admin', 'Administrator')
)


class CustomUser(AbstractUser):

    username = None
    email = models.EmailField(_('email address'), unique=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    fullname = models.CharField(max_length=150)
    email_validation = models.BooleanField(default=False)
    profile = models.CharField(max_length=11, choices=PROFILE, default='normal')

    def __str__(self):
        return self.email


class LoginAdmin(models.Model):

    objects = models.Manager()

    pin = models.CharField(max_length=6, default=Util.create_pin())
    validated = models.BooleanField(default=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    created_at = models.CharField(max_length=19)
    valid_until = models.CharField(max_length=19)
    active = models.BooleanField(default=True)
