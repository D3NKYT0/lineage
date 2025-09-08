from django.urls import path
from .views import *


app_name = 'message'


urlpatterns = [
    path('index/', message, name='index'),
    path('send-friend-request/<int:user_id>/', send_friend_request, name='send_friend_request'),
    path('accept-friend-request/<int:friendship_id>/', accept_friend_request, name='accept_friend_request'),
    path('reject-friend-request/<int:friendship_id>/', reject_friend_request, name='reject_friend_request'),
    path('cancel-friend-request/<int:friendship_id>/', cancel_friend_request, name='cancel_friend_request'),
    path('remove-friend/<int:friendship_id>/', remove_friend, name='remove_friend'),
    path('friends-list/', friends_list, name='friends_list'),

    # URLs AJAX mantidas apenas para funcionalidades não relacionadas ao chat
    path('api/search-users/', search_users_ajax, name='search_users_ajax'),
]
