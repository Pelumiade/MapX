from django.dispatch import receiver
from .models import FieldOfficer, Farmland, ActivityLog
from django.db.models.signals import post_save
from django.dispatch import receiver
from .signals import farmland_mapped, field_officer_created


@receiver(field_officer_created, sender=FieldOfficer)
def create_field_officer_activity_log(sender, instance, created, **kwargs):
    if created:
        # Field Officer created an entry
        ActivityLog.objects.create(user=instance.created_by, action_type='created a field officer', platform='web', country=instance.country)

@receiver(farmland_mapped, sender=Farmland)
def create_farmland_activity_log(sender, instance, created, **kwargs):
    if created:
        # Farmland mapped an entry
        ActivityLog.objects.create(user=instance.field_officer.user, action_type='mapped a farmland', platform='web', country=instance.country)
