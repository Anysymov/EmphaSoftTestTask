from django.contrib import admin
from django.urls import path
from MainApp import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path("", views.rooms_list),
    path("rooms/", views.rooms_list),
    path("profile/", views.user_profile),
    path("profile/<room>/<date>/", views.user_profile),
    path("profile_entrance/", views.profile_entrance),
    path("profile_entrance/register/", views.user_register),
    path("reservation/<name>/", views.room_reservation),
    path("reservation/", views.room_reservation),
    path("profile/logout/", views.profile_logout),
    path('roomsAPI/', views.RoomList.as_view(), name='room-list'),
    path('roomsAPI/<int:rm>/', views.RoomDetail.as_view(), name='room-detail'),
    path('userAPI/', views.UserList.as_view(), name='user-list'),
    path('userAPI/<int:us>/', views.UserDetail.as_view(), name='user-detail'),
    path('reservationAPI/', views.Reservationist.as_view(), name='reservation-list'),
    path('reservationAPI/<int:rv>/', views.ReservationDetail.as_view(), name='reservation-detail'),
]
