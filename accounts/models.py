from django.db import models

# Create your models here.

from django.contrib.auth.models import (AbstractBaseUser, BaseUserManager,
                                        PermissionsMixin)

from base.managers import MyUserManager, ActiveUserManager
from django.dispatch import receiver
from django.urls import reverse
#from django_rest_passwordreset.signals import reset_password_token_created
from django.core.mail import send_mail  
from phonenumber_field.modelfields import PhoneNumberField


class User(AbstractBaseUser, PermissionsMixin):
    """ Custom user model that supports using email instead of username"""
   
    email = models.EmailField(max_length=255, unique=True, verbose_name="email address")
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    is_admin = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    designation =  models.CharField(max_length=100)
    phone_number = PhoneNumberField(unique=True, null=True)
    picture = models.ImageField(upload_to='accounts/media', blank=True, null=True)
    location = models.CharField(max_length=255, null=True, blank=True)
    verification_code = models.CharField(max_length=100, null=True, blank=True)

    REQUIRED_FIELDS= []
    USERNAME_FIELD = "email"
    
    objects = MyUserManager()
    active_objects = ActiveUserManager()

    def __str__(self):
        return self.email 
    
    @property
    def picture_url(self):
        try:
            url = self.picture.url
        except:
            url =''
        return url
    
    @property
    def is_admin(self):
        return self.is_staff


    