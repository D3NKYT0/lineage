from django.urls import path
from . import views

app_name = 'licence'

urlpatterns = [
    # Dashboard e gerenciamento
    path('', views.dashboard, name='dashboard'),
    path('list/', views.license_list, name='list'),
    path('create/', views.license_create, name='create'),
    path('<int:license_id>/', views.license_detail, name='detail'),
    path('<int:license_id>/edit/', views.license_edit, name='edit'),
    path('<int:license_id>/activate/', views.license_activate, name='activate'),
    path('<int:license_id>/deactivate/', views.license_deactivate, name='deactivate'),
    path('<int:license_id>/reactivate/', views.license_reactivate, name='reactivate'),
    path('<int:license_id>/renew/', views.license_renew, name='renew'),
    path('<int:license_id>/delete/', views.license_delete, name='delete'),
    path('status/', views.status, name='status'),
    path('test-block/', views.test_block, name='test_block'),
    
    # API URLs
    path('api/activate/', views.api_activate_license, name='api_activate'),
    path('api/status/', views.api_license_status, name='api_status'),
    path('api/features/', views.api_license_features, name='api_features'),
]
