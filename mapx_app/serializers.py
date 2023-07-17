from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.reverse import reverse

from .models import FieldOfficer, Farmer, Farmland, Location, Country, State
from .models import ActivityLog
from collections import OrderedDict
from base.constants import CREATED, MAPPED

User = get_user_model()


class FarmerListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()

    class Meta:
        model = Farmer
        fields = ['id', 'name','folio_id', 'phone',
                    'address', 'assigned_field_officer', 'is_mapped', 'country']
   
    def get_name(self, obj):
        return f'{obj.first_name} {obj.last_name}'

    def get_address(self, obj):
        return f'{obj.location.city},{obj.location.state}'
    
    def get_country(self, obj):
        return obj.location.country.name


class FarmerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        exclude = ['folio_id', 'assigned_field_officer', 'picture', 'is_mapped']


class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        fields = ['id', 'first_name', 'last_name', 'phone', 'email', 'location']


class FarmlandCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmland
        fields = ['size', 'area', 'farm_address', 'farm_name']


class LongLatSerializer(serializers.Serializer):
    longitude = serializers.FloatField(write_only=True)
    latitude = serializers.FloatField(write_only=True)


class MapFarmlandSerializer(serializers.Serializer):
    point = LongLatSerializer(many=True, write_only=True)
    

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        exclude = ['verification_code', 'is_active', 'is_staff', 'is_superuser', 'last_login', 'groups', 'user_permissions', 'designation', 'password', 'picture']


class LocationSerializer(serializers.ModelSerializer):

    class Meta:
        model = Location
        fields = ['country', 'state', 'city']


class FieldOfficerSerializer(serializers.ModelSerializer):
    delete_url = serializers.SerializerMethodField()
    update_url = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    num_farmers_assigned = serializers.SerializerMethodField()
    num_farms_mapped = serializers.SerializerMethodField()
    location = serializers.PrimaryKeyRelatedField(queryset=Location.objects.all())
    email = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['email', 'country', 'full_name', 'first_name', 'last_name', 
                  'phone_number', 'num_farmers_assigned', 'num_farms_mapped',
                    'delete_url', 'update_url', 'picture','location']
        
    def get_email(self, obj):
        return obj.user.email
    
    def get_full_name(self, obj) -> str:
        return f"{obj.first_name} {obj.last_name}"

    def get_country(self, obj):
        return f"{obj.feo.location.state.name}  {obj.feo.location.country.name}"

    def get_delete_url(self, obj) -> str:
        request = self.context.get('request')
        if request is None:
            return None
        return reverse("mapx_app:fieldofficer_delete",  kwargs={"id": obj.id}, request=request)

    def get_update_url(self, obj) -> str:
        request = self.context.get('request')
        if request is None:
            return None
        return reverse("mapx_app:fieldofficer_update", kwargs={"id": obj.id}, request=request)

    def get_num_farmers_assigned(self, obj) -> str:
        return obj.feo.num_farmers_assigned

    def get_num_farms_mapped(self, obj) -> str:
        return obj.feo.num_farms_mapped

        
class NewFieldSerializer(serializers.ModelSerializer):
    user = UserSerializer()
    location = serializers.PrimaryKeyRelatedField(
        queryset=Location.objects.all())
    delete_url = serializers.SerializerMethodField()
    update_url = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    num_farmers_assigned = serializers.SerializerMethodField()
    num_farms_mapped = serializers.SerializerMethodField()
    progress_level = serializers.ReadOnlyField()
    location_detail = serializers.SerializerMethodField()


    class Meta:
        model = FieldOfficer
        fields = ['user', 'full_name', 'country',
                  'num_farmers_assigned', 'num_farms_mapped', 'location','progress_level', 'delete_url', 'update_url', 'location_detail']
        
    def get_full_name(self, obj) -> str:
        if isinstance(obj, OrderedDict): 
            return f"{obj['user'].first_name} {obj['user'].last_name}"
        else:
            return f"{obj.user.first_name} {obj.user.last_name}"

    def get_country(self, obj):
        if isinstance(obj, OrderedDict):
            return obj['location'].country.name
        else:
            return obj.location.country.name

    def get_delete_url(self, obj) -> str:
        if isinstance(obj, OrderedDict):
            return None
        else:
            request = self.context.get('request')
            if request is None:
                return None
            return reverse("mapx_app:fieldofficer_delete",  kwargs={"id": obj.id}, request=request)
        
    def get_update_url(self, obj) -> str:
        if isinstance(obj, OrderedDict):
            return None
        else:
            request = self.context.get('request')
            if request is None:
                return None
            return reverse("mapx_app:fieldofficer_update", kwargs={"id": obj.id}, request=request)
    
    def get_num_farmers_assigned(self, obj) -> str:
        if isinstance(obj, OrderedDict):
            return 0
        else:
            return obj.num_farmers_assigned

    
    def get_num_farms_mapped(self, obj) -> str:
        if isinstance(obj, OrderedDict):
            return 0
        else:
            return obj.num_farms_mapped

    def get_location_detail(self, obj):
        if isinstance(obj, OrderedDict):
            return f"{obj['location'].city}, {obj['location'].cstate.name}"
        return f'{obj.location.city}, {obj.location.state.name}'
    
    # def to_representation(self, instance):
    #     data = super().to_representation(instance)
    #     request = self.context.get('request')
    #     if request.method == 'GET' and 'user' in data:
    #         del data['user']['first_name']
    #         del data['user']['last_name']
    #     return data

    def update(self, instance, validated_data):
        user_data = validated_data.pop('user', None)
        location = validated_data.pop('location', None)

        if user_data:
            user_serializer = UserSerializer(
                instance.user, data=user_data, partial=True)
            user_serializer.is_valid(raise_exception=True)
            user_serializer.save()

        if location:
            instance.location = location

        return super().update(instance, validated_data)
    
    # def create(self, validated_data):
    #     field_officer = FieldOfficer.objects.create(**validated_data)
    #     return field_officer

    # def update(self, instance, validated_data):
    #     instance.picture = validated_data.get('picture', instance.picture)
    #     instance.first_name = validated_data.get('first_name', instance.first_name)
    #     instance.last_name = validated_data.get('last_name', instance.last_name)
    #     instance.email = validated_data.get('email', instance.email)
    #     instance.phone_number = validated_data.get('phone_number', instance.phone_number)
    #     instance.country = validated_data.get('country', instance.country)
    #     instance.state = validated_data.get('state', instance.state)
    #     instance.city = validated_data.get('city', instance.city)
    #     instance.save()

    #     return instance
    
    # def to_representation(self, instance):
    #     representation = super().to_representation(instance)
    #     if self.context['request'].method in ['GET', 'HEAD']:
    #         # Exclude fields during listing
    #         del representation['first_name']
    #         del representation['last_name']
    #         del representation['state']
    #         del representation['city']
    #     return representation
    

class FarmlandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmland
        fields = '__all__' 


class AdminSerializer(serializers.Serializer):
    name = serializers.SerializerMethodField()
    is_admin = serializers.SerializerMethodField()
    last_login = serializers.DateTimeField()

    def get_name(self, obj):
        return obj.get_full_name()

    def get_is_admin(self, obj):
        return "Admin" if obj.is_admin else "Not Admin"


class AdminFieldOfficerSerializer(serializers.ModelSerializer):
    class Meta:
        model = FieldOfficer
        fields = ['first_name','last_name' , 'location']


class AdminFarmlandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmland
        fields = ['farm_name', 'farm_address']


class ActivityLogSerializer(serializers.ModelSerializer):
    actor = serializers.PrimaryKeyRelatedField(queryset=User.objects.all())
    activity = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    actor_name = serializers.SerializerMethodField()
    user_type = serializers.SerializerMethodField()
    platform = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = ['id', 'actor', 'actor_name',
                  'date', 'status', 'user_type', 'platform', 'country', 'activity']

    def get_activity(self, obj) -> str:
        if obj.action_type == CREATED:
            return 'created an feo'
        elif obj.action_type == MAPPED:
            return 'mapped a farmland'
        
    def get_date(self, obj) -> str:
        date = obj.timestamp
        formatted_date = date.strftime('%m/%d/%Y %I:%M%p')
        return formatted_date

    def get_country(self, obj) -> str:
        if obj.action_type == MAPPED:
            print(obj)
            return obj.content_object.field_officer.location.country.name
        return obj.content_object.location.country.name
    
    def get_platform(self, obj) -> str:
        return 'Web'
    
    def get_user_type(self, obj) -> str:
        if hasattr(obj.actor, 'admin'):
            return 'Admin'
        return 'FEO'

    def get_actor_name(self, obj) -> str:
        return obj.actor.get_full_name()
    

class CountryListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Country
        fields = "__all__"


class StatesListSerializer(serializers.ModelSerializer):

    class Meta:
        model = State
        fields = "__all__"


class LocationCityListSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Location
        fields = ["id", 'city']