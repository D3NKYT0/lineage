from django.urls import path
from .views import *


app_name = 'auditor'


urlpatterns = [
    path('', AuditorPageView.as_view(), name='auditor'),
    path('data/', auditor_data_view, name='auditor-data'),
]
