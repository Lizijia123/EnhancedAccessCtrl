from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('target-app/', target_app, name='target_app'),

    path('api-lists/', get_api_lists, name='get_api_lists'),
    path('user-api-list/', update_user_api_list, name='update_user_api_list'),
    path('api/discovery/', api_discovery, name='api_discovery'),
]
