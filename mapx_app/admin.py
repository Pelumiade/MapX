from django.contrib import admin

# Register your models here.
from .models import (
    FieldOfficer, Farmer, Farmland, Admin, Country, State, Location, Coordinate
)

# class FieldOfficerAdmin(admin.ModelAdmin):
#     list_display = ('firstname', 'lastname','phone_number', 'country', 'state', 'city', 'location', 'num_farmers_assigned', 'num_farms_mapped', 'progress_level')
#     search_fields = ('firstname', 'lastname', 'phone_number', 'country', 'state', 'city', 'location', 'num_farmers_assigned', 'num_farms_mapped', 'progress_level')
#     list_filter = ('country', 'state', 'city')
#     fieldsets = (
#         (None, {
#             'fields': ('first_name', 'last_name', 'email', 'phone_number', 'country', 'state', 'city', 'location')
#         }),
#     )

#     def get_fieldsets(self, request, obj=None):
#         fieldsets = super().get_fieldsets(request, obj)
#         if obj:  # Editing an existing field officer
#             fieldsets += (
#                 ('Statistics', {
#                     'fields': ('num_farmers_assigned', 'num_farms_mapped', 'progress_level'),
#                 }),
#             )
#         return fieldsets

admin.site.register(FieldOfficer)
admin.site.register(Farmer)
admin.site.register(Farmland)
admin.site.register(Admin)
admin.site.register(Country)
admin.site.register(State)
admin.site.register(Location)
admin.site.register(Coordinate)
