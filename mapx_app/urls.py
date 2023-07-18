from django.urls import path

from .views import (FieldOfficerCreateAPIView, FieldOfficerUpdateAPIView, FarmerCreateView, 
                    FarmerListAPIView, FarmerDetailAPIView, 
                    FarmlandCreateAPIView, ActivityLogListAPIView, 
                    FieldOfficerListView, FieldOfficerDeleteAPIView, MapFarmlandAPIView, 
                    FieldOfficerExportAPIView, RecentFieldOfficersAPIView,
                    LocationCityListAPIView, FieldOfficerRankingAPIView, 
                   StatesListAPIView, GlobalDashboardAPIView, CountryListAPIView)

app_name = 'mapx_app'

urlpatterns = [
    
    path('farmers/create/', FarmerCreateView.as_view(), name='farmer_create'),
    path('farmers/list/', FarmerListAPIView.as_view(), name='farmer_list'),
    path('farmers/<int:pk>/', FarmerDetailAPIView.as_view(), name='farmer_detail'),
    path('farmland/<int:farmer_id>/create/', FarmlandCreateAPIView.as_view(), name='farmland_create'),
    path('farmland/<int:pk>/map/', MapFarmlandAPIView.as_view(), name='map_farmland'),

    path('admin/fieldofficers/create/', FieldOfficerCreateAPIView.as_view(), name='fieldofficer_create'),
    path('admin/fieldofficers/<int:id>/update/', FieldOfficerUpdateAPIView.as_view(), name='fieldofficer_update'),
    path('fieldofficer/<int:id>/delete/', FieldOfficerDeleteAPIView.as_view(), name='fieldofficer_delete'),
    path('admin/fieldofficers/list/', FieldOfficerListView.as_view(), name='field_officer_list'),
    path('activitylog/', ActivityLogListAPIView.as_view(), name='activity_log'),
    path('countries/', CountryListAPIView.as_view(), name='countries'),
    path('countries/<int:country_pk>/state', StatesListAPIView.as_view(), name='states'),
    path('state/<int:state_pk>/cities', LocationCityListAPIView.as_view(), name="cities"),
    path('admin/dashboard/', GlobalDashboardAPIView.as_view(), name='admind_ashboard'),
    path('recent/feo/', RecentFieldOfficersAPIView.as_view(), name='recent_feo'),
    path('feo/ranking/', FieldOfficerRankingAPIView.as_view(), name='feo_ranking'),
    path('export_table/', FieldOfficerExportAPIView.as_view(), name='export_table')
   

]