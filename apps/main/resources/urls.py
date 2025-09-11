from django.urls import path
from . import views

app_name = 'resources'

urlpatterns = [
    path('', views.resources_dashboard, name='dashboard'),
    path('toggle/<str:resource_name>/', views.toggle_resource, name='toggle'),
    path('category/<str:category>/', views.resources_by_category, name='by_category'),
]
