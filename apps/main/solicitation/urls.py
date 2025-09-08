from django.urls import path
from .views import *


app_name = 'solicitation'


urlpatterns = [
    path('', SolicitationListView.as_view(), name='solicitation_list'),
    path('create/', SolicitationCreateView.as_view(), name='create'),
    path('<str:protocol>/dashboard/', SolicitationDashboardView.as_view(), name='solicitation_dashboard'),
    path('<str:protocol>/status/update/', SolicitationStatusUpdateView.as_view(), name='status_update'),
    path('<str:protocol>/historico/adicionar/', AddEventToHistoryView.as_view(), name='add_event_to_history'),
    path('<str:protocol>/detalhes/', SolicitationDashboardView.as_view(), name='solicitation_dashboard'),
]
