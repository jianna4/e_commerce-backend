

# Create your models here.
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from .manager import UserManager

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    full_name = models.CharField(max_length=255)

    phone_number = models.CharField(max_length=20, blank=True, null=True)
    mpesa_number = models.CharField(max_length=20, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)   # staff/admin
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email
    

class County(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="county")
    
    def __str__(self):
        return self.name
    

class PickupPoint(models.Model):
    name = models.CharField(max_length=255)
    location = models.ForeignKey(County, on_delete=models.CASCADE, related_name="pickup_points")
    opening_hours = models.CharField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.name