from django.urls import path
from . import views

app_name = 'calendary'

urlpatterns = [
    path('dashboard/', views.calendar, name="calendar"),
    path('api/events/', views.get_events, name="get_events"),
]
