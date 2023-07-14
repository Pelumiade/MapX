import uuid
from pytz import country_names
from datetime import datetime

from django.contrib.auth import get_user_model
from django.db import models
from django.core.mail import send_mail
from django.conf import settings

from accounts.models import User


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin")
    location = models.ForeignKey(
        'mapx_app.Location', on_delete=models.SET_NULL, null=True)


class FieldOfficer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="feo")
    # country = models.CharField(max_length=50)
    # state = models.CharField(max_length=50)
    # city = models.CharField(max_length=50)
    location = models.ForeignKey(
        'mapx_app.Location', on_delete=models.SET_NULL, null=True)
    num_farmers_assigned = models.PositiveIntegerField(default=0)
    num_farms_mapped = models.PositiveIntegerField(default=0)
     
    #progress level
    @property
    def progress_level(self):
        total_assigned = self.num_farmers_assigned
        total_mapped = self.num_farms_mapped

        if total_assigned > 0:
            progress = (total_mapped / total_assigned) * 100
        else:
            progress = 0

        return progress

    # def save(self, *args, **kwargs):
    #     if not self.pk:
    #         # Generate a random password for new Field Officers
    #         password = User.objects.make_random_password()

    #         # Create a User account for the Field Officer
    #         user = User.objects.create_user(email=self.email, password=password)
    #         self.user = user

    #         # Send email with login details
    #         subject = "Login Details for Mapping App"
    #         message = f"Dear {self.first_name},\n\nYour account has been created for the Mapping App.\n\nEmail: {self.email}\nPassword: {password}\n\nPlease log in using the provided credentials.\n\nBest regards,\nThe Mapping App Team"
    #         send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])

    #     super().save(*args, **kwargs)
    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class Farmer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    folio_id = models.CharField(max_length=10, unique=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255, unique=True, verbose_name="email address")
    assigned_field_officer = models.ForeignKey(FieldOfficer, on_delete=models.SET_NULL, null=True)
    location = models.ForeignKey('Location', on_delete=models.SET_NULL, null=True)
    picture = models.ImageField(upload_to='media/')
    is_mapped = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def save(self, *args, **kwargs):
        if not self.folio_id:
            self.folio_id = self.generate_folio_id()
        super().save(*args, **kwargs)

    def generate_folio_id(self):
        unique_id = uuid.uuid4().hex[:8]  # Generate a unique identifier
        current_year = datetime.now().year
        #time_now = datetime.now().strftime("%H%M%S")
        folio_id = f"AM{current_year}{unique_id}"
        return folio_id[:10]  # Trim the folio_id to 10 characters

    @property
    def is_mapped(self):
        return self.farmlands.filter(is_mapped=True).exists()
    

class Farmland(models.Model):
    farm_name = models.CharField(max_length=100, null=True, blank=True)
    field_officer = models.ForeignKey(FieldOfficer,on_delete=models.SET_NULL, null=True)
    farmer= models.ForeignKey(Farmer, on_delete=models.SET_NULL, null=True, related_name='farmlands')
    size = models.DecimalField(max_digits=8, decimal_places=2)
    area = models.CharField(max_length=20)
    longitude = models.FloatField()
    latitude = models.FloatField()
    picture = models.ImageField(upload_to='media/')
    farm_address = models.CharField(max_length=250)
    is_mapped = models.BooleanField(default=False)


class Country(models.Model):

    COUNTRY_CHOICES = [
        (country, country) for code, country in country_names.items()
    ]
    name = models.CharField(max_length=150, choices=COUNTRY_CHOICES)


class State(models.Model):
    name = models.CharField(max_length=50)


class City(models.Model):
    name = models.CharField(max_length=50)


class Location(models.Model):
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    city = models.ForeignKey(City, on_delete=models.SET_NULL, null=True)


class ActivityLog(models.Model):
    ACTION_CHOICES = [
        ('created_fo', 'Created a Field Officer'),
        ('mapped_farm', 'Mapped a Farmland'),
        # Add more choices for other actions
    ]

    USER_TYPE_CHOICES = [
        ('admin', 'Admin'),
        ('field_officer', 'Field Officer'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE)
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES)
    action_type = models.CharField(max_length=20, choices=ACTION_CHOICES)
    platform = models.CharField(max_length=20)
    country = models.CharField(max_length=50)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user} - {self.get_action_type_display()}'

    class Meta:
        ordering = ['-timestamp']


