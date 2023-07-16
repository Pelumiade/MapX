from django.db import models
from django.contrib.auth.models import (AbstractBaseUser, PermissionsMixin)

from base.managers import MyUserManager, ActiveManager
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractBaseUser, PermissionsMixin):
    """ Custom user model that supports using email instead of username"""
    
    email = models.EmailField(max_length=255, unique=True, verbose_name="email address")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    designation =  models.CharField(max_length=100)
    phone_number = PhoneNumberField(unique=True, null=True)
    picture = models.ImageField(upload_to='media/', blank=True, null=True)
    verification_code = models.CharField(max_length=10, null=True, blank=True)

    REQUIRED_FIELDS= []
    USERNAME_FIELD = "email"
    
    objects = MyUserManager()
    active_objects = ActiveManager()

    class Meta:
        indexes = [
            models.Index(fields=["last_name", "first_name", "email"]),
        ]
    
    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'


    