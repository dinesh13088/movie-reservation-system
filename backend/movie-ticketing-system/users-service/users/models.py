from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import CustomUserManager
# Create your models here.
class CustomUser(AbstractUser):
    email=models.EmailField("email address",unique=True)
    fullname=models.CharField(max_length=50)
    keycloak_id=models.CharField(max_length=500)
    objects=CustomUserManager()
    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = ["fullname"]

    def __str__(self):
        return self.email

