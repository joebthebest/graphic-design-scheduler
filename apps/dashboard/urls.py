from django.urls import path
from . import views

urlpatterns = [
    path('', views.designer_dashboard_view, name='designer_dashboard'),
    path('appointment/<str:booking_ref>/status/', views.update_appointment_status_view, name='update_appointment_status'),
    path('availability/', views.working_hours_settings_view, name='working_hours_settings'),
    path('export/csv/', views.export_appointments_csv_view, name='export_appointments_csv'),
]
