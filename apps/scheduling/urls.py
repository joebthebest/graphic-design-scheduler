from django.urls import path
from . import views

urlpatterns = [
    path('book/', views.book_wizard_view, name='book_wizard'),
    path('book/<slug:service_slug>/', views.book_wizard_view, name='book_wizard_service'),
    path('api/available-slots/', views.available_slots_api_view, name='available_slots_api'),
    path('confirmation/<str:booking_ref>/', views.booking_success_view, name='booking_success'),
    path('calendar-invite/<str:booking_ref>/download/', views.download_ics_view, name='download_ics'),
    path('lookup/', views.lookup_booking_view, name='lookup_booking'),
    path('booking/<str:booking_ref>/', views.booking_detail_view, name='booking_detail'),
    path('booking/<str:booking_ref>/reschedule/', views.reschedule_booking_view, name='reschedule_booking'),
    path('booking/<str:booking_ref>/cancel/', views.cancel_booking_view, name='cancel_booking'),
    path('booking/<str:booking_ref>/review/', views.add_review_view, name='add_review'),
]
