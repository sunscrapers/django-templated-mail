from django.db import models
from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    locale = models.CharField(max_length=5)
