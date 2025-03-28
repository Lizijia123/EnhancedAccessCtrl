# urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('user-info/', get_user_info, name='get_user_info'),

    path('register/', register, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),

    path('target-app-list/', get_target_app_list, name='get_target_app_list'),
    path('v1/target-app-list/', get_target_app_list_pagely, name='get_target_app_list_pagely'),
    path('target-app/', target_app, name='target_app'),

    path('api-lists/', get_api_lists, name='get_api_lists'),
    path('v1/api-lists/', get_api_lists_pagely, name='get_api_lists_pagely'),
    path('user-api-list/', update_user_api_list, name='update_user_api_list'),
    path('v1/user-api-list/', update_user_api_list_v1, name='update_user_api_list_v1'),

    path('api-discovery/start/', start_api_discovery, name='api_discovery'),
    path('api-discovery/finish/', finish_api_discovery, name='finish_api_discovery'),
    path('api-discovery/cancel/', cancel_api_discovery, name='cancel_api_discovery'),
    path('api-discovery/notification/', api_discovery_notification, name='api_discovery_notification'),
    path('api-discovery/status/', get_auto_API_discovery_status, name='api_discovery_status'),
    path('api-discovery/manual/status/', get_manual_API_discovery_status, name='get_manual_API_discovery_status'),

    path('model-construct/', construct_model, name='construct_model'),
    path('model-construct/data-collection-status/', get_data_collection_status, name='get_data_collection_status'),

    path('detection/features/', detect_feature, name='detect_feature'),
    path('detection/config/', detection_config, name='detection_config'),
    path('detection/start/', start_detection, name='start_detection'),
    path('detection/pause/', pause_detection, name='pause_detection'),

    path('detection/report/', get_detection_report, name='get_detection_report'), # 废弃接口，后续需要迁移
    path('v1/detection/report/', get_detection_report_v1, name='get_detection_report_v1'),
    path('detection/records/', get_detection_records, name='get_detection_records'), # 废弃接口，后续需要迁移
    path('detection/records/byIds/', get_detection_records_by_ids, name='get_detection_records_by_ids'),
    path('v1/detection/records/', get_detection_records_v1, name='get_detection_records_v1'),
    path('detection/traffic-data-list/', get_traffic_data_list, name='get_traffic_data_list'),


    path('detection/record/api/', get_detection_records_by_api, name='get_detection_records_by_api'),

    path('load_target_app/', load_target_app, name='load_target_app'),

    path('check-deployment/', check_deployment, name='check_deployment'),
]
