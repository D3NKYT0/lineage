from django.urls import path
from . import views


app_name = "tops"


urlpatterns = [
    # Home
    path('public/tops/', views.TopsHomeView.as_view(), name='home'),
    
    # Rankings
    path('public/tops/pvp/', views.TopsPvpView.as_view(), name='pvp'),
    path('public/tops/pk/', views.TopsPkView.as_view(), name='pk'),
    path('public/tops/adena/', views.TopsAdenaView.as_view(), name='adena'),
    path('public/tops/clans/', views.TopsClansView.as_view(), name='clans'),
    path('public/tops/level/', views.TopsLevelView.as_view(), name='level'),
    path('public/tops/online/', views.TopsOnlineView.as_view(), name='online'),
    path('public/tops/olympiad/', views.TopsOlympiadView.as_view(), name='olympiad'),
    path('public/tops/siege/', views.TopsSiegeView.as_view(), name='siege'),
]
