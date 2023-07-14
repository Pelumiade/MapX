from rest_framework import serializers
from .models import FieldOfficer, Farmer, Farmland
from rest_framework import serializers
from .models import ActivityLog
from rest_framework.reverse import reverse
from django.contrib.auth import get_user_model

User = get_user_model()


class FarmerListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()

    class Meta:
        model = Farmer
        fields = ['id', 'name', 'first_name', 'last_name', 'folio_id', 'phone',  'address']
   
    def get_name(self, obj):
        if hasattr(obj, 'first_name') and hasattr(obj, 'last_name'):
            if 'request' in self.context:
                request = self.context['request']
                if request.method == 'GET':
                    # Combine first_name and last_name for GET request (listing)
                    return f"{obj.first_name} {obj.last_name}"
        # Return None or a default value if 'first_name' and 'last_name' attributes are not available
        return None
    
    def get_address(self, obj):

        if hasattr(obj, 'state') and hasattr(obj, 'city'):
            if 'request' in self.context:
                request = self.context['request']
                if request.method == 'GET':
                    # Combine state and city for GET request (listing)
                    return f"{obj.state}, {obj.city}"
        # Return None or a default value if 'state' and 'city' attributes are not available
        return None
    

class FarmerCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        exclude = ['folio_id', 'assigned_field_officer']


class FarmerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmer
        fields = ['id', 'first_name', 'last_name', 'phone', 'email', 'location']


class FarmlandCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmland
        fields = ['size', 'area', 'longitude', 'latitude', 'picture', 'farm_address']

        
class FieldOfficerSerializer(serializers.ModelSerializer):
    delete_url = serializers.SerializerMethodField()
    update_url = serializers.SerializerMethodField()
    country = serializers.SerializerMethodField()
    full_name = serializers.SerializerMethodField()
    num_farmers_assigned = serializers.SerializerMethodField()
    num_farms_mapped = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = ['email', 'country', 'full_name', 'first_name', 'last_name', 
                  'phone_number', 'num_farmers_assigned', 'num_farms_mapped',
                    'delete_url', 'update_url', 'picture']



    # def get_name(self, obj):
    #     if hasattr(obj, 'first_name') and hasattr(obj, 'last_name'):
    #         if 'request' in self.context:
    #             request = self.context['request']
    #             if request.method == 'GET':
    #                 # Combine first_name and last_name for GET request (listing)
    #                 return f"{obj.first_name} {obj.last_name}"
    #     # Return None or a default value if 'first_name' and 'last_name' attributes are not available
    #     return None

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
    user = serializers.CharField(source='user.first_name')
    user_type = serializers.SerializerMethodField()

    class Meta:
        model = ActivityLog
        fields = ['user', 'user_type', 'action_type', 'platform', 'country', 'timestamp']

    def get_user_type(self, obj):
        if obj.user.is_superuser:
            return 'admin'
        elif hasattr(obj.user, 'fieldofficer'):
            return 'field_officer'
        else:
            return 'unknown'


