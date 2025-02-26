# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('target-app-list/', get_target_app_list, name='get_target_app_list'),
    path('target-app/', target_app, name='target_app'),

    path('api-lists/', get_api_lists, name='get_api_lists'),
    path('user-api-list/', update_user_api_list, name='update_user_api_list'),
    path('api/discovery/', api_discovery, name='api_discovery'),
    path('api/discovery/finish', finish_api_discovery, name='finish_api_discovery'),
    path('api/discovery/cancel', cancel_api_discovery, name='cancel_api_discovery'),
    path('api/discovery/notification/', api_discovery_notification, name='api_discovery_notification'),

    path('api/discovery/status/', get_auto_API_discovery_status, name='api_discovery_status'),

    path('detection/features/', detect_feature, name='detect_feature'),
    path('model/construct/', construct_model, name='construct_model'),

    path('detection/config/', detection_config, name='detection_config'),
    path('detection/start/', start_detection, name='start_detection'),
    path('detection/pause/', pause_detection, name='pause_detection'),

    path('detection/record/combination', get_detection_records_by_combination,
         name='get_detection_records_by_combination'),
    path('detection/record/api', get_detection_records_by_api, name='get_detection_records_by_api'),
]
