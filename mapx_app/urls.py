from .views import  FieldOfficerCreateAPIView, FieldOfficerUpdateAPIView, FarmerCreateView,  FarmerListAPIView, FarmerDetailAPIView, FarmlandCreateAPIView, AdminProfileAPIView, ActivityLogListAPIView, FieldOfficerListAPIView, FieldOfficerDeleteAPIView

from django.urls import path
app_name = 'mapx_app'

urlpatterns = [
    # FieldOfficer URLs
   # path('fieldofficers/', FieldOfficerListCreateView.as_view(), name='fieldofficer-list-create'),
    # Farmer URLs
    path('farmers/create/', FarmerCreateView.as_view(), name='farmer_create'),
    path('farmers/list/', FarmerListAPIView.as_view(), name='farmer_list'),
    path('farmers/<int:pk>/', FarmerDetailAPIView.as_view(), name='farmer_detail'),
    path('farmland/<int:farmer_id>/create/', FarmlandCreateAPIView.as_view(), name='farmland_create'),

    # Admin URLs
    path('admin/fieldofficers/create/', FieldOfficerCreateAPIView.as_view(), name='fieldofficer_create'),
    path('admin/fieldofficers/<int:id>/update/', FieldOfficerUpdateAPIView.as_view(), name='fieldofficer_update'),
    path('fieldofficer/<int:id>/delete/', FieldOfficerDeleteAPIView.as_view(), name='fieldofficer_delete'),
    path('admin/fieldofficers/list/', FieldOfficerListAPIView.as_view(), name='field_officer_list'),
    path('admin/profile/', AdminProfileAPIView.as_view(), name='admin_profile_api'),
    path('activitylog/', ActivityLogListAPIView.as_view(), name='activity_log'),
]