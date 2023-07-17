from .models import FieldOfficer
from django.conf import settings
from django.core.mail import send_mail
from django.db import models
from django.db.models import Count
from rest_framework import generics, status, filters
from rest_framework.generics import DestroyAPIView, ListAPIView
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from django_filters.rest_framework import DjangoFilterBackend

from .models import FieldOfficer, Farmer, Farmland, ActivityLog, Coordinate, Location, Country, State, Admin
from . import serializers
from .serializers import (FieldOfficerSerializer, FarmerSerializer, MapFarmlandSerializer, FarmerCreateSerializer,
                          FarmerListSerializer, FarmlandSerializer, FarmlandCreateSerializer, AdminSerializer,
                          AdminFieldOfficerSerializer, AdminFarmlandSerializer, ActivityLogSerializer,
                          NewFieldSerializer, CountryListSerializer)
from .permissions import IsSuperuserOrAdminUser, IsFieldOfficerUser
from accounts.models import User
from base.constants import CREATED, MAPPED, SUCCESS
from base.mixins import ActivityLogMixin
from base.pagination import StandardResultsSetPagination


class AdminDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperuserOrAdminUser]

    def get(self, request):
        # Total number of field officers
        field_officer_count = FieldOfficer.objects.all().count()

        # Total number of mapped farmlands
        mapped_farmland_count = Farmland.objects.filter(is_mapped=True).count()

        # Total number of unmapped farmlands
        unmapped_farmland_count = Farmland.objects.filter(is_mapped=False).count()

        # # Total number of highest farmland in a region (country)
        # highest_farmland_country = Farmland.objects.values('country').annotate(count=models.Count('id')).order_by('-count').first()

        # Total number of registered farmers
        registered_farmer_count = Farmer.objects.all().count()

        total_cities = Location.objects.all().count()

        # Field officer ranking
        field_officer_ranking = FieldOfficer.objects.annotate(
            registered_farmer_count=models.Count('farmer'),
            mapped_farmland_count=models.Count('farmer__farmland', filter=models.Q(farmer__farmland__is_mapped=True)),
            progress_level=models.ExpressionWrapper(models.F('mapped_farmland_count') / models.F('registered_farmer_count'), output_field=models.FloatField()),
        ).values('name', 'registered_farmer_count', 'mapped_farmland_count', 'progress_level').order_by('-registered_farmer_count')

        # Number of recently added field officers
        recently_added_field_officers = FieldOfficer.objects.order_by('-id')[:5]

        data = {
            'field_officer_count': field_officer_count,
            'mapped_farmland_count': mapped_farmland_count,
            'unmapped_farmland_count': unmapped_farmland_count,
            # 'highest_farmland_country': highest_farmland_country['country'] if highest_farmland_country else None,
            'registered_farmer_count': registered_farmer_count,
            'field_officer_ranking': field_officer_ranking,
            'recently_added_field_officers': FieldOfficerSerializer(recently_added_field_officers, many=True).data,
        }

        return Response(data)
    

class GlobalAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperuserOrAdminUser]
    def get_field_officer_count(self):
        count = FieldOfficer.objects.count()
        return count

    def get_mapped_farmlands_count(self):
        count = Farmland.objects.filter(is_mapped=True).count()
        return count

    def get_unmapped_farmlands_count(self):
        count = Farmland.objects.filter(is_mapped=False).count()
        return count

    def get_highest_mapped_country(self):
        country = Farmland.objects.values('farmer__location__country__name').annotate(
            count=Count('id')).order_by('-count').first()
        return country['farmer__location__country__name'] if country else None

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
    

# class RecentFieldOfficerAPIView(APIView):
#     permission_classes = [IsAuthenticated, IsSuperuserOrAdminUser]
#     def get_recent_field_officers(self, admin_id):
#         admin = Admin.objects.get(id=admin_id)
#         recent_field_officers = FieldOfficer.objects.filter(
#             user__admin=admin).order_by('-id')[:3]
#         return recent_field_officers

#     def get(self, request, admin_id):
#         recent_field_officers = self.get_recent_field_officers(admin_id)

#         data = []
#         for field_officer in recent_field_officers:
#             field_officer_data = {
#                 'name': f'{field_officer.user.first_name} {field_officer.user.last_name}',
#                 'location': str(field_officer.location),
#             }
#             data.append(field_officer_data)

#         return Response(data)




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



class FieldOfficerListView(generics.ListAPIView):
    queryset = FieldOfficer.objects.filter(is_deleted=False).order_by('id')
    serializer_class = NewFieldSerializer
    permission_classes = [IsAuthenticated, IsSuperuserOrAdminUser]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['location__country__name']
    search_fields = ['first_name', 'last_name',
                     'country', 'email']
    
    # def get_queryset(self):
    #     return super().get_queryset().filter(is_deleted=False)



#Field Officer
class FarmerCreateView(generics.CreateAPIView):
    queryset = Farmer.objects.all()
    serializer_class = FarmerCreateSerializer
    permission_classes = [IsAuthenticated, IsFieldOfficerUser]
    
    def perform_create(self, serializer):
        field_officer = self.request.user.feo  # Get the field officer associated with the request user
        serializer.save(assigned_field_officer=field_officer)

  
class FarmerListAPIView(generics.ListAPIView):
    serializer_class = FarmerListSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        if hasattr(self.request.user, 'admin'):
            return Farmer.objects.all()
        return Farmer.objects.filter(assigned_field_officer=self.request.user.feo)
    
  
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
        farmland.is_mapped = True
        farmland.save()
        return Response({'message': 'Farmland has been mapped succesfully'}, status=status.HTTP_200_OK)


class FarmerDetailAPIView(generics.RetrieveAPIView):
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer
    permission_classes = [IsAuthenticated, IsFieldOfficerUser, IsSuperuserOrAdminUser]
   

#Admin
class FieldOfficerCreateAPIView(ActivityLogMixin, generics.CreateAPIView):
    queryset = FieldOfficer.objects.all()
    serializer_class = NewFieldSerializer
    permission_classes = [IsSuperuserOrAdminUser]

    def post(self, request, *args, **kwargs):
        request.data['action'] = CREATED
        return super().post(request, *args, **kwargs)


    def perform_create(self, serializer):
        location = serializer.validated_data.pop("location")
        user_data= serializer.validated_data.pop('user')
        user_dict = dict(user_data)
        
        password = User.objects.make_random_password()
        print(password)
        user = User.objects.create_user(**user_dict, password=password)

        serializer.validated_data['user'] = user
        serializer.validated_data['location'] = location

        feo = FieldOfficer.objects.create(user=user, location=location)
        self.created_obj=feo

        subject = "Login Details for MapX App"
        message = f"Dear {user.first_name},\n\nYour account has been created for the MapX App.\n\nEmail: {user.email}\nPassword: {password}\n\nPlease log in using the provided credentials.\n\nBest regards,\nThe MapX App Team"
        send_mail(subject, message,
                  settings.DEFAULT_FROM_EMAIL, [user.email])
        return Response({'message': 'Field Officer created successfully'}, status=status.HTTP_201_CREATED)


class FieldOfficerUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = NewFieldSerializer
    queryset = FieldOfficer.objects.all()
    permission_classes = [IsAuthenticated, IsSuperuserOrAdminUser]
    lookup_field = 'id'


# class FieldOfficerListAPIView(generics.ListAPIView):
#     queryset = FieldOfficer.objects.all()
#     serializer_class = FieldOfficerSerializer
#     permission_classes = [IsAdminUser]


# class FieldOfficerDeleteAPIView(DestroyAPIView):
#     queryset = FieldOfficer.objects.all()
#     lookup_field = 'id'

#     def perform_destroy(self, instance):
#         instance.user.is_active = False
#         instance.save()

class FieldOfficerDeleteAPIView(APIView):
    permission_classes=[IsSuperuserOrAdminUser]

    def delete(self, request, id):
        try:
            field_officer = FieldOfficer.objects.get(id=id)
            field_officer.is_deleted = True
            field_officer.save()
            return Response({'message': 'Field Officer was deleted successfully'}, status=status.HTTP_204_NO_CONTENT)  # Success, no content
        except FieldOfficer.DoesNotExist:
            return Response(status=404)  # FieldOfficer not found
        

class AdminProfileAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]



    def get(self, request):
        user = request.user  # Get the current logged-in user (admin)

        # Retrieve the data for the admin section
        admin_serializer = AdminSerializer(user)

        # Retrieve the data for the profile section
        profile_data = {
            'designation': user.designation,
            'email': user.email,
            'phone_number': user.PhoneNumber,
            'location': user.location,
        }

        # Retrieve the data for the recent field officers section
        field_officers = FieldOfficer.objects.order_by('-id')[:3]  # Retrieve the three most recent field officers
        field_officer_serializer = AdminFieldOfficerSerializer(field_officers, many=True)

        # Retrieve the data for the recent mapped farmland section
        mapped_farmlands = Farmland.objects.filter(is_mapped=True).order_by('-id')[:3]  # Retrieve the three most recent mapped farmlands
        farmland_serializer = AdminFarmlandSerializer(mapped_farmlands, many=True)

        data = {
            'admin': admin_serializer.data,
            'profile': profile_data,
            'recent_field_officers': field_officer_serializer.data,
            'recent_mapped_farmlands': farmland_serializer.data,
        }

        return Response(data)
    

class ActivityLogListAPIView(ListAPIView):
    serializer_class = ActivityLogSerializer
    queryset = ActivityLog.objects.all()
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return super().get_queryset().filter(status=SUCCESS)


class CountryListAPIView(ListAPIView):
    queryset = Country.objects.all()
    serializer_class = CountryListSerializer


class StatesListAPIView(ListAPIView):
    queryset = State.objects.all()
    serializer_class = serializers.StatesListSerializer

    def get_queryset(self, *args, **kwargs):
        country_pk = self.kwargs["country_pk"]
        return super().get_queryset().filter(country_id=country_pk)
    

class LocationCityListAPIView(ListAPIView):
    queryset = Location.objects.all()
    serializer_class = serializers.LocationCityListSerializer

    def get_queryset(self, *args, **kwargs):
        state_pk = self.kwargs["state_pk"]
        return super().get_queryset().filter(state_id=state_pk)
