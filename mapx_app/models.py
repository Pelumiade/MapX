from django.db import models

# Create your models here.
from django.contrib.auth.models import User
from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
import uuid
from django.contrib.auth import get_user_model


User = get_user_model()

class FieldOfficer(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="feo")
    picture = models.ImageField(upload_to='media/')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    email = models.EmailField(max_length=255, unique=True, verbose_name="email address")
    phone_number = models.CharField(max_length=20)
    country = models.CharField(max_length=50)
    state = models.CharField(max_length=50)
    city = models.CharField(max_length=50)
    num_farmers_assigned = models.PositiveIntegerField(default=0)
    num_farms_mapped = models.PositiveIntegerField(default=0)
    progress_level = models.IntegerField(editable=False)
    is_deleted = models.BooleanField(default=False)
    location = models.CharField(max_length=255, null=True, blank=True)


    class Meta:
        indexes = [
            models.Index(fields=["last_name", "first_name", "email"]),
        ]
    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
        return f'{self.first_name} {self.last_name}'
    
    def delete(self, *args, **kwargs):
        self.is_deleted = True
        self.save()

    def undelete(self):
        self.is_deleted = False
        self.save()

    @property
    def is_active(self):
        return not self.is_deleted
    
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

    def save(self, *args, **kwargs):
        if not self.pk:
            # Generate a random password for new Field Officers
            password = User.objects.make_random_password()

            # Create a User account for the Field Officer
            user = User.objects.create_user(email=self.email, password=password)
            self.user = user

            # Send email with login details
            subject = "Login Details for Mapping App"
            message = f"Dear {self.first_name},\n\nYour account has been created for the Mapping App.\n\nEmail: {self.email}\nPassword: {password}\n\nPlease log in using the provided credentials.\n\nBest regards,\nThe Mapping App Team"
            send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [self.email])

        super().save(*args, **kwargs)
        

class Farmer(models.Model):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    folio_id = models.CharField(max_length=10, unique=True)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255, unique=True, verbose_name="email address")
    assigned_field_officer = models.ForeignKey(FieldOfficer, on_delete=models.SET_NULL, null=True)
    country = models.CharField(max_length=50)
    state =  models.CharField(max_length=50)
    city =  models.CharField(max_length=50)
    picture = models.ImageField(upload_to='media/')
    is_mapped = models.BooleanField(default=False)

    def __str__(self):
        return self.get_full_name()

    def get_full_name(self):
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
    farmer= models.ForeignKey(Farmer, on_delete=models.CASCADE)
    size = models.DecimalField(max_digits=8, decimal_places=2)
    area = models.CharField(max_length=50)
    longitude = models.FloatField()
    latitude = models.FloatField()
    picture = models.ImageField(upload_to='media/')
    farm_address = models.CharField(max_length=250)


from django.db import models
from django.contrib.auth import get_user_model

User = get_user_model()

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


