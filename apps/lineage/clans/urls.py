from django.urls import path
from . import views

app_name = 'clans'

urlpatterns = [
    path('', views.ClanListView.as_view(), name='list'),
    path('dashboard/', views.ClanDashboardView.as_view(), name='dashboard'),
    path('test-claim/', views.TestClaimClanView.as_view(), name='test_claim'),
    path('<int:clan_id>/', views.ClanDetailView.as_view(), name='detail'),
    path('<int:clan_id>/apply/', views.ApplyToClanView.as_view(), name='apply'),
    path('application/<int:pk>/<str:action>/', views.ProcessApplicationView.as_view(), name='process_application'),
]
