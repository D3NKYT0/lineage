from django.urls import path

from .views import *

app_name = 'administrator'

urlpatterns = [
  path('administrator/chat/<str:group_name>/', chat_room, name='chat_room'),
  path('administrator/error/chat/', error_chat, name='error_chat'),

  path('page/<path:file_name>/', serve_theme_file, name='serve_theme_file'),
  path('security/settings/', security_settings, name='security_settings'),
]
