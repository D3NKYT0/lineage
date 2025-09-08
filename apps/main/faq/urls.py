from django.urls import path
from .views import faq_list


app_name = 'faq'


urlpatterns = [
    path('', faq_list, name='faq_list'),
]
