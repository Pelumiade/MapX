from tablib import Dataset
from django.http import HttpResponse
from django.conf import settings
from django.core.mail import send_mail
from django.db.models import Count
from rest_framework import generics, status, filters
from rest_framework.generics import ListAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend
from .models import FieldOfficer, Farmer, Farmland, ActivityLog, Coordinate, Location, Country, State
from . import serializers
from datetime import datetime
from django.contrib.auth import get_user_model
from .serializers import (FarmerSerializer, MapFarmlandSerializer, FarmerCreateSerializer,
                          FarmerListSerializer,  FarmlandCreateSerializer,  ActivityLogSerializer,
                          NewFieldSerializer, CountryListSerializer)

from .permissions import IsSuperuserOrAdminUser, IsFieldOfficerUser
from accounts.models import User
from base.constants import CREATED, MAPPED, SUCCESS
from base.mixins import ActivityLogMixin
from base.pagination import StandardResultsSetPagination


#DASHBOARD
class GlobalDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperuserOrAdminUser]
    def get_field_officer_count(self):
        count = FieldOfficer.objects.filter(is_deleted=False).count()
        return count

    def get_mapped_farmlands_count(self):
        count = Farmland.objects.filter(is_mapped=True).count()
        return count

    def get_unmapped_farmlands_count(self):
        count = Farmer.objects.filter(is_mapped=False).count()
        return count

    def get_highest_mapped_country(self):
        country_count = Farmland.objects.values('farmer__location__country').annotate(
            count=Count('id')).order_by('-count').first()

        if country_count:
            count = country_count['count']
            return count
        else:
            return None

    def get_total_farmers(self):
        count = Farmer.objects.count()
        return count

    def get_total_cities(self):
        count = Location.objects.values('city').distinct().count()
        return count

    def get(self, request):
        field_officer_count = self.get_field_officer_count()
        mapped_farmlands_count = self.get_mapped_farmlands_count()
        unmapped_farmlands_count = self.get_unmapped_farmlands_count()
        highest_mapped_country = self.get_highest_mapped_country()
        total_farmers = self.get_total_farmers()
        total_cities = self.get_total_cities()

        data = {
            'field_officer_count': field_officer_count,
            'mapped_farmlands_count': mapped_farmlands_count,
            'unmapped_farmlands_count': unmapped_farmlands_count,
            'highest_mapped_country': highest_mapped_country,
            'total_farmers': total_farmers,
            'total_cities': total_cities
        }
        return Response(data)
    

#CREATE FEO
class FieldOfficerCreateAPIView(ActivityLogMixin, generics.CreateAPIView):
    queryset = FieldOfficer.objects.all()
    serializer_class = NewFieldSerializer
    permission_classes = [IsSuperuserOrAdminUser]

    def post(self, request, *args, **kwargs):
        request.data['action'] = CREATED
        return super().post(request, *args, **kwargs)

    def perform_create(self, serializer):
        location = serializer.validated_data.pop("location")
        user_data = serializer.validated_data.pop('user')
        user_dict = dict(user_data)

        password = User.objects.make_random_password()
        user = User.objects.create_user(**user_dict, password=password)

        serializer.validated_data['user'] = user
        serializer.validated_data['location'] = location

        feo = FieldOfficer.objects.create(user=user, location=location)
        self.created_obj = feo

        subject = "Login Details for MapX App"
        message = f"Dear {user.first_name},\n\nYour account has been created for the MapX App.\n\nEmail: {user.email}\nPassword: {password}\n\nPlease log in using the provided credentials.\n\nBest regards,\nThe MapX App Team"
        send_mail(subject, message,
                  settings.DEFAULT_FROM_EMAIL, [user.email])
        return Response({'message': 'Field Officer created successfully'}, status=status.HTTP_201_CREATED)
    

# RECENT FEO CREATED
class RecentFieldOfficersAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperuserOrAdminUser]

    def get(self, request):
        recent_field_officers = FieldOfficer.objects.order_by('-id')[:3]

        data = []
        for field_officer in recent_field_officers:
            field_officer_data = {
                'name': f'{field_officer.user.first_name} {field_officer.user.last_name}',
                'location': str(field_officer.location),
            }
            data.append(field_officer_data)

        return Response(data)
    
    
#FEO RANKING
class FieldOfficerRankingAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperuserOrAdminUser]
    def get_top_field_officers(self):
        top_field_officers = FieldOfficer.objects.all()
        return top_field_officers

    def get(self, request):
        top_field_officers = self.get_top_field_officers()

        data = []
        for field_officer in top_field_officers:
            total_farmer_assigned = field_officer.farmers.count()
            total_farm_mapped = field_officer.farmlands.count()

            if total_farmer_assigned > 0:
                progress_level = (total_farm_mapped /
                                  total_farmer_assigned) * 100
            else:
                progress_level = 0

            field_officer_data = {
                'name': f'{field_officer.user.first_name} {field_officer.user.last_name}',
                'registered_farmers': total_farmer_assigned,
                'mapped_farmlands': total_farm_mapped,
                'progress_level': progress_level,
            }
            data.append(field_officer_data)

        # Sort field officers based on progress level in descending order
        data.sort(key=lambda x: x['progress_level'], reverse=True)

        # Get the top 3 field officers
        top_3_field_officers = data[:3]

        return Response(top_3_field_officers)


#TO UPDATE FEO
class FieldOfficerUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = NewFieldSerializer
    queryset = FieldOfficer.objects.all()
    permission_classes = [IsAuthenticated, IsSuperuserOrAdminUser]
    lookup_field = 'id'


#TO DELETE FEO
class FieldOfficerDeleteAPIView(APIView):
    permission_classes = [IsSuperuserOrAdminUser]

    def delete(self, request, id):
        try:
            field_officer = FieldOfficer.objects.get(id=id)
            field_officer.is_deleted = True
            field_officer.save()
            # Success, no content
            return Response({'message': 'Field Officer was deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except FieldOfficer.DoesNotExist:

            # FieldOfficer not found
            return Response({'message': 'Field Officer was not found'}, status=status.HTTP_404_NOT_FOUND)


#LIST OF FEO
class FieldOfficerListView(generics.ListAPIView):
    queryset = FieldOfficer.objects.filter(is_deleted=False).order_by('id')
    serializer_class = NewFieldSerializer
    permission_classes = [IsAuthenticated, IsSuperuserOrAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['location__country__name']
    search_fields = ['first_name', 'last_name',
                     'country', 'email']
    

#EXPORT TABLE
class FieldOfficerExportAPIView(APIView):
    permission_classes = [IsSuperuserOrAdminUser]

    def get(self, request):
        # Get the list of field officers
        field_officers = FieldOfficer.objects.all()

        # Create a tabular dataset using the tablib library
        dataset = Dataset()

        # Add the headers to the dataset
        dataset.headers = ['First Name', 'Last Name', 'Location',
                           'Num Farmers Assigned', 'Num Farms Mapped', 'Progress Level']

        # Add the field officer data to the dataset
        for field_officer in field_officers:
            dataset.append([
                field_officer.user.first_name,
                field_officer.user.last_name,
                field_officer.location.city,
                field_officer.num_farmers_assigned,
                field_officer.num_farms_mapped,
                field_officer.progress_level,
            ])

        # Create the response with the exported dataset
        response = HttpResponse(dataset.csv, content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="field_officers.csv"'

        return response
   

#CREATE FARMERS
class FarmerCreateView(generics.CreateAPIView):
    queryset = Farmer.objects.all()
    serializer_class = FarmerCreateSerializer
    permission_classes = [IsAuthenticated, IsFieldOfficerUser]
    
    def perform_create(self, serializer):
        field_officer = self.request.user.feo  # Get the field officer associated with the request user
        serializer.save(assigned_field_officer=field_officer)

        field_officer.num_farmers_assigned += 1
        field_officer.save()



#LIST OF FARMERS 
class FarmerListAPIView(generics.ListAPIView):
    serializer_class = FarmerListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'admin'):
            return Farmer.objects.all()
        return Farmer.objects.filter(assigned_field_officer=self.request.user.feo)
    

#CREATE FARMLAND FOR FARMERS 
class FarmlandCreateAPIView(generics.CreateAPIView):
    queryset = Farmland.objects.all()
    serializer_class = FarmlandCreateSerializer
    permission_classes = [IsAuthenticated, IsFieldOfficerUser]
  
    def post(self, request, *args, **kwargs):
        return super().post(request, *args, **kwargs)
    
    def perform_create(self, serializer):
        farmer_id = self.kwargs['farmer_id']
        farmer = Farmer.objects.get(id=farmer_id)
        farmland = serializer.save(farmer=farmer)
        return Response({'message': 'Farmland created successfully'}, status=status.HTTP_201_CREATED)
    
    
#MAP A FARMLAND
class MapFarmlandAPIView(ActivityLogMixin, generics.UpdateAPIView):
    queryset = Farmland.objects.all()
    serializer_class = MapFarmlandSerializer
    lookup_field = 'pk'

    def update(self, request, *args, **kwargs):
        request.data['action'] = MAPPED
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        farmland = self.get_object()
        self.created_obj = farmland
        lat_list = serializer.validated_data['point']

        for coordinate in lat_list:
            Coordinate.objects.create(**coordinate, farmland=farmland)

        # Get the field officer associated with the request user
        field_officer = self.request.user.feo
        farmland.field_officer = field_officer

        field_officer.num_farms_mapped += 1
        field_officer.save()

        farmland.is_mapped = True
        farmland.save()
        return Response({'message': 'Farmland has been mapped succesfully'}, status=status.HTTP_200_OK)


#GET FARMERS DETAIL  
class FarmerDetailAPIView(generics.RetrieveAPIView):
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer
    permission_classes = [IsAuthenticated, IsFieldOfficerUser, IsSuperuserOrAdminUser]
   

#ACTIVITY LOG
class ActivityLogListAPIView(ListAPIView):
    serializer_class = ActivityLogSerializer
    queryset = ActivityLog.objects.all()
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return super().get_queryset().filter(status=SUCCESS)

#COUNTRY
class CountryListAPIView(ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountryListSerializer


#STATE
class StatesListAPIView(ListAPIView):
    queryset = State.objects.all()
    serializer_class = serializers.StatesListSerializer

    def get_queryset(self, *args, **kwargs):
        country_pk = self.kwargs["country_pk"]
        return super().get_queryset().filter(country_id=country_pk)
    
#LOCATION
class LocationCityListAPIView(ListAPIView):
    queryset = Location.objects.all()
    serializer_class = serializers.LocationCityListSerializer

    def get_queryset(self, *args, **kwargs):
        state_pk = self.kwargs["state_pk"]
        return super().get_queryset().filter(state_id=state_pk)


