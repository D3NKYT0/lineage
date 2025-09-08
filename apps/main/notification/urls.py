from django.urls import path
from . import views
from .views import send_push_view

app_name = 'notification'

urlpatterns = [
    path('list/', views.get_notifications, name='notification_list'),
    path('mark-all-as-read/', views.mark_all_as_read, name='mark_all_as_read'),
    path('clear-all-notifications/', views.clear_all_notifications, name='clear_all_notifications'),
    path('detail/<int:pk>/', views.notification_detail, name='notification_detail'),
    path('all/', views.all_notifications, name='all_notifications'),
    path('confirm-view/<int:pk>/', views.confirm_notification_view, name='confirm_notification_view'),
    path('send-push/', send_push_view, name='send_push'),
]
