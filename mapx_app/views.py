from django.shortcuts import render

# Create your views here.
from django.db import models
from rest_framework import generics
from .models import FieldOfficer, Farmer, Farmland, ActivityLog
from .serializers import FieldOfficerSerializer, FarmerSerializer, FarmerCreateSerializer, FarmerListSerializer, FarmlandSerializer,  FarmlandCreateSerializer, AdminSerializer, AdminFieldOfficerSerializer, AdminFarmlandSerializer, ActivityLogSerializer
from rest_framework.generics import DestroyAPIView
from .permissions import IsSuperuserOrAdminUser, IsFieldOfficerUser
from rest_framework.permissions import IsAdminUser, IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from accounts.models import User
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import FieldOfficer, Farmland, Farmer
from .serializers import FieldOfficerSerializer


class AdminDashboardAPIView(APIView):
    permission_classes = [IsAuthenticated, IsSuperuserOrAdminUser]

    def get(self, request):
        # Total number of field officers
        field_officer_count = FieldOfficer.objects.count()

        # Total number of mapped farmlands
        mapped_farmland_count = Farmland.objects.filter(is_mapped=True).count()

        # Total number of unmapped farmlands
        unmapped_farmland_count = Farmland.objects.filter(is_mapped=False).count()

        # Total number of highest farmland in a region (country)
        highest_farmland_country = Farmland.objects.values('country').annotate(count=models.Count('id')).order_by('-count').first()

        # Total number of registered farmers
        registered_farmer_count = Farmer.objects.count()

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
            'highest_farmland_country': highest_farmland_country['country'] if highest_farmland_country else None,
            'registered_farmer_count': registered_farmer_count,
            'field_officer_ranking': field_officer_ranking,
            'recently_added_field_officers': FieldOfficerSerializer(recently_added_field_officers, many=True).data,
        }

        return Response(data)


class FieldOfficerListCreateView(generics.ListCreateAPIView):
    queryset = FieldOfficer.objects.all()
    serializer_class = FieldOfficerSerializer
    permission_classes = [IsAuthenticated, IsAdminUser]


#Field Officer
class FarmerCreateView(generics.CreateAPIView):
    queryset = Farmer.objects.all()
    serializer_class = FarmerCreateSerializer
    permission_classes = [IsAuthenticated, IsFieldOfficerUser]

    def perform_create(self, serializer):
        field_officer = self.request.user.fieldofficer  # Get the field officer associated with the request user
        serializer.save(assigned_field_officer=field_officer)

    # Increase the number of assigned farmers for the field officer
        field_officer.num_farmers_assigned += 1
        field_officer.save()

  
class FarmerListAPIView(generics.ListAPIView):
    queryset = Farmer.objects.all()
    serializer_class = FarmerListSerializer
    permission_classes = [IsAuthenticated, IsFieldOfficerUser, IsSuperuserOrAdminUser]

    def get_queryset(self):
        field_officer = self.request.user.fieldofficer
        queryset = self.queryset.filter(assigned_field_officer=field_officer)
        return queryset
    
  
class FarmlandCreateAPIView(generics.CreateAPIView):
    serializer_class = FarmlandCreateSerializer
    permission_classes = [IsAuthenticated,IsFieldOfficerUser]

    
    def perform_create(self, serializer):
        farmer_id = self.kwargs['farmer_id']
        farmer = Farmer.objects.get(id=farmer_id)
        field_officer = self.request.user.fieldofficer  # Get the field officer associated with the request user
        serializer.save(farmer=farmer, field_officer=field_officer)

        # Increase the number of mapped farmlands for the field officer
        field_officer.num_farms_mapped += 1
        field_officer.save()

        # Update the is_mapped status of the farmer
        farmer.is_mapped = True
        farmer.save()


class FarmerDetailAPIView(generics.RetrieveAPIView):
    queryset = Farmer.objects.all()
    serializer_class = FarmerSerializer
    permission_classes = [IsAuthenticated, IsFieldOfficerUser, IsSuperuserOrAdminUser]
   

#Admin
class FieldOfficerCreateAPIView(generics.CreateAPIView):
    queryset = FieldOfficer.objects.all()
    serializer_class = FieldOfficerSerializer
    permission_classes = [IsAdminUser]


class FieldOfficerUpdateAPIView(generics.RetrieveUpdateAPIView):
    serializer_class = FieldOfficerSerializer
    queryset = FieldOfficer.objects.all()
    permission_classes = [IsAdminUser, IsAuthenticated]  
    lookup_field = 'id'


class FieldOfficerListAPIView(generics.ListAPIView):
    queryset = FieldOfficer.objects.all()
    serializer_class = FieldOfficerSerializer
    permission_classes = [IsAdminUser]


class FieldOfficerDeleteAPIView(DestroyAPIView):
    queryset = FieldOfficer.objects.all()
    lookup_field = 'id'

    def perform_destroy(self, instance):
        instance.is_deleted = True
        instance.save()


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
    

class ActivityLogListAPIView(APIView):
    permission_classes = [IsAuthenticated, IsAdminUser]
    def get(self, request):
        logs = ActivityLog.objects.all()
        serializer = ActivityLogSerializer(logs, many=True)
        return Response(serializer.data)
