from rest_framework import serializers
from .models import FieldOfficer, Farmer, Farmland
from rest_framework import serializers
from .models import ActivityLog
from rest_framework.reverse import reverse

class FarmerListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()

    class Meta:
        model = Farmer
        fields = ['id', 'name', 'firstname', 'lastname', 'folio_id', 'phone',  'address', 'email', 'country', 'state', 'city']
   
    def get_name(self, obj):
        if hasattr(obj, 'firstname') and hasattr(obj, 'lastname'):
            if 'request' in self.context:
                request = self.context['request']
                if request.method == 'GET':
                    # Combine firstname and lastname for GET request (listing)
                    return f"{obj.firstname} {obj.lastname}"
        # Return None or a default value if 'firstname' and 'lastname' attributes are not available
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
        fields = ['id', 'firstname', 'lastname', 'phone', 'email',  'country', 'state', 'city']


class FarmlandCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmland
        fields = ['size', 'area', 'longitude', 'latitude', 'picture', 'farm_address']

        
class FieldOfficerSerializer(serializers.ModelSerializer):
    delete_url = serializers.SerializerMethodField()
    update_url = serializers.SerializerMethodField()
    location = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    
    class Meta:
        model = FieldOfficer
        fields = ['email', 'location', 'name', 'firstname', 'lastname', 'email', 'phone_number', 'country', 'state' , 'city', 'num_farmers_assigned', 'num_farms_mapped', 'progress_level', 'delete_url', 'update_url', 'picture']
        read_only_fields = ['delete_url', 'update_url', 'location', 'name']


    def get_name(self, obj):
        if hasattr(obj, 'firstname') and hasattr(obj, 'lastname'):
            if 'request' in self.context:
                request = self.context['request']
                if request.method == 'GET':
                    # Combine firstname and lastname for GET request (listing)
                    return f"{obj.firstname} {obj.lastname}"
        # Return None or a default value if 'firstname' and 'lastname' attributes are not available
        return None
    
    def get_location(self, obj):

        if hasattr(obj, 'state') and hasattr(obj, 'city'):
            if 'request' in self.context:
                request = self.context['request']
                if request.method == 'GET':
                    # Combine state and city for GET request (listing)
                    return f"{obj.state}, {obj.city}"
        # Return None or a default value if 'state' and 'city' attributes are not available
        return None

    def get_delete_url(self, obj):
        request = self.context.get('request')
        if request is None:
            return None
        return reverse("mapx_app:fieldofficer_delete",  kwargs={"id": obj.id}, request=request)
        
    def get_update_url(self, obj):
        request = self.context.get('request')
        if request is None:
            return None
        return reverse("mapx_app:fieldofficer_update", kwargs={"id": obj.id}, request=request)
    

    def create(self, validated_data):
        field_officer = FieldOfficer.objects.create(**validated_data)
        return field_officer

    def update(self, instance, validated_data):
        instance.picture = validated_data.get('picture', instance.picture)
        instance.firstname = validated_data.get('firstname', instance.firstname)
        instance.lastname = validated_data.get('lastname', instance.lastname)
        instance.email = validated_data.get('email', instance.email)
        instance.phone_number = validated_data.get('phone_number', instance.phone_number)
        instance.country = validated_data.get('country', instance.country)
        instance.state = validated_data.get('state', instance.state)
        instance.city = validated_data.get('city', instance.city)
        instance.save()

        return instance
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if self.context['request'].method in ['GET', 'HEAD']:
            # Exclude fields during listing
            del representation['firstname']
            del representation['lastname']
            del representation['state']
            del representation['city']
        return representation
    

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
        fields = ['firstname','lastname' ,'state', 'country']


class AdminFarmlandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Farmland
        fields = ['farm_name', 'farm_address']


class ActivityLogSerializer(serializers.ModelSerializer):
    user = serializers.CharField(source='user.firstname')
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


