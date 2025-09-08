from django.urls import path
from . import views

app_name = 'downloads'

urlpatterns = [
    path('public/downloads/', views.DownloadListView.as_view(), name='download_list'),
    path('public/downloads/download/<int:pk>/', views.download_redirect, name='download_redirect'),
    path('app/downloads/', views.InternalDownloadListView.as_view(), name='internal_download_list'),
    path('app/downloads/download/<int:pk>/', views.download_redirect, name='internal_download_redirect'),
] 