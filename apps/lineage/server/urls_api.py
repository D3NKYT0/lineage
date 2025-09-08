from django.urls import path
from .views.accounts_api import (
    AccountDashboardAPI,
    UpdatePasswordAPI,
    RegisterLineageAccountAPI,
    LinkLineageAccountAPI,
    RequestLinkByEmailAPI,
    LinkByEmailTokenAPI,
)

urlpatterns = [
    path('accounts/dashboard/', AccountDashboardAPI.as_view(), name='api_account_dashboard'),
    path('accounts/update_password/', UpdatePasswordAPI.as_view(), name='api_update_password'),
    path('accounts/register/', RegisterLineageAccountAPI.as_view(), name='api_register_lineage_account'),
    path('accounts/link/', LinkLineageAccountAPI.as_view(), name='api_link_lineage_account'),
    path('accounts/request_link/', RequestLinkByEmailAPI.as_view(), name='api_request_link_by_email'),
    path('accounts/link_by_token/', LinkByEmailTokenAPI.as_view(), name='api_link_by_email_token'),
] 
