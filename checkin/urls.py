from urllib import request

from django.urls import path

from . import views


urlpatterns = [
    path('checkin/', views.CheckInView.as_view(), name='checkin'),
    path('singleCheckin/<int:pk>/', views.SingleCheckin.as_view(), name='singleCheckin'),
    path('delete_checkin/<int:pk>/', views.DeleteCheckin.as_view(), name='delete_checkin'),
]