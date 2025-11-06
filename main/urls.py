from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('rooms/', views.rooms, name='rooms'),
    path('rooms/<int:room_id>/', views.room_detail, name='room_detail'),
    path('gallery/', views.gallery, name='gallery'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('booking/', views.booking, name='booking'),
    path('booking/success/<int:booking_id>/', views.booking_success, name='booking_success'),
    path('check-availability/', views.check_availability, name='check_availability'),
    path('reports/bookings/', views.booking_report, name='booking_report'),
]

# was orginal urlpatterns


# from django.urls import path
# from . import views

# urlpatterns = [
#     path('', views.home, name='home'),
#     path('rooms/', views.rooms, name='rooms'),
#     path('gallery/', views.gallery, name='gallery'),
#     path('about/', views.about, name='about'),
#     path('contact/', views.contact, name='contact'),
#     path('booking/', views.booking, name='booking'),
# ]

