# tasks.py
from celery import shared_task
import requests
from django.http import JsonResponse
from .models import TargetApplication
from .views import validate_and_save_api
from django.utils import timezone

@shared_task
def handle_api_discovery_notification(app_id, discovery_data):
    try:
        target_app = TargetApplication.objects.get(id=app_id)
        discovered_api_list_data = discovery_data.get('discovered_API_list', [])

        # 更新 discovered_API_list
        for api in target_app.discovered_API_list.all():
            api.path_segment_list.all().delete()
            api.request_param_list.all().delete()
            api.request_data_fields.all().delete()
            api.delete()
        target_app.discovered_API_list.clear()
        for api_data in discovered_api_list_data:
            result = validate_and_save_api(api_data)
            if isinstance(result, JsonResponse):
                continue
            target_app.discovered_API_list.add(result)

        # 更新 user_API_list
        if len(list(target_app.user_API_list.all())) == 0:
            for api_data in discovered_api_list_data:
                target_app.user_API_list.add(validate_and_save_api(api_data))

        # 更新状态
        if target_app.detect_state == 'API_LIST_TO_DISCOVER':
            target_app.detect_state = 'API_LIST_TO_IMPROVE'
            target_app.save(update_fields=['detect_state'])
        target_app.last_API_discovery_at = timezone.now()
        target_app.save(update_fields=['last_API_discovery_at'])

        return {'message': 'API discovery and update successful'}
    except Exception as e:
        return {'error': str(e)}