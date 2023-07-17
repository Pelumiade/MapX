import uuid
from datetime import datetime
from pytz import country_names

from django.contrib.auth import get_user_model
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.core.mail import send_mail
from django.conf import settings

from accounts.models import User
from base.constants import ACTION_STATUS, SUCCESS


class Admin(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="admin")
    location = models.ForeignKey(
        'mapx_app.Location', on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f'{self.user.first_name} {self.user.last_name}'


class FieldOfficer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="feo")
    location = models.ForeignKey(
        'mapx_app.Location', on_delete=models.SET_NULL, null=True)
    num_farmers_assigned = models.PositiveIntegerField(default=0)
    num_farms_mapped = models.PositiveIntegerField(default=0)
    progress_level= models.IntegerField(editable=False)
     
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
    
    
class Farmland(models.Model):
    farm_name = models.CharField(max_length=100, null=True, blank=True)
    field_officer = models.ForeignKey(FieldOfficer,on_delete=models.SET_NULL, null=True)
    farmer= models.ForeignKey(Farmer, on_delete=models.SET_NULL, null=True, related_name='farmlands')
    size = models.DecimalField(max_digits=8, decimal_places=2)
    area = models.CharField(max_length=20)
    picture = models.ImageField(upload_to='media/')
    farm_address = models.CharField(max_length=250)
    is_mapped = models.BooleanField(default=False)


class Country(models.Model):
    COUNTRY_CHOICES = [
        (country, country) for code, country in country_names.items()]
    name = models.CharField(max_length=150, choices=COUNTRY_CHOICES)

    def __str__(self):
        return self.name
    

class State(models.Model):
    name = models.CharField(max_length=50)
    country = models.ForeignKey(Country, on_delete=models.CASCADE, related_name='states', null=True)

    def __str__(self) -> str:
        return self.name


class Location(models.Model):
    country = models.ForeignKey(Country, on_delete=models.SET_NULL, null=True)
    state = models.ForeignKey(State, on_delete=models.SET_NULL, null=True)
    city = models.CharField(max_length=50, null=True)

    def __str__(self) -> str:
        return f"{self.city}"
    

class ActivityLog(models.Model):
    actor = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    action_type = models.CharField(max_length=20)
    timestamp = models.DateTimeField(auto_now_add=True)
    content_type = models.ForeignKey(ContentType, models.SET_NULL, blank=True, null=True)
    object_id = models.PositiveIntegerField(blank=True, null=True)
    status = models.CharField(choices=ACTION_STATUS, max_length=7, default=SUCCESS)
    content_object = GenericForeignKey()

    def __str__(self):
        return f'{self.action_type} by {self.actor}'

    class Meta:
        ordering = ['-timestamp']


class Coordinate(models.Model):
    farmland = models.ForeignKey(Farmland, on_delete=models.CASCADE, related_name="coordinates")
    longitude = models.FloatField()
    latitude = models.FloatField()

    def __str__(self) -> str:
        return f"Longitude: {self.longitude} Latitude: {self.latitude}"
