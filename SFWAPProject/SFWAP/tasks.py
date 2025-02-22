import logging
from celery import shared_task
from .views import *
from django.utils import timezone
from typing import Dict, List

logger = logging.getLogger(__name__)


@shared_task
def handle_api_discovery_notification(app_id, discovery_data):
    try:
        target_app = TargetApplication.objects.get(id=app_id)
        discovered_api_list_data = discovery_data.get('discovered_API_list', [])

        # 更新 discovered_API_list
        error_response = save_api_list(target_app, 'discovered_API_list', discovered_api_list_data)
        if error_response:
            return error_response

        # 更新 user_API_list
        if len(list(target_app.user_API_list.all())) == 0:
            error_response = save_api_list(target_app, 'user_API_list', discovered_api_list_data)
            if error_response:
                return error_response

        # 更新状态
        if target_app.detect_state == 'API_LIST_TO_DISCOVER':
            target_app.detect_state = 'API_LIST_TO_IMPROVE'
            target_app.save(update_fields=['detect_state'])
        target_app.last_API_discovery_at = timezone.now()
        target_app.save(update_fields=['last_API_discovery_at'])

        return {'message': 'API discovery and update successful'}
    except TargetApplication.DoesNotExist:
        logger.error(f"Target application with id {app_id} not found.")
        return {'error': f"Target application with id {app_id} not found."}
    except Exception as e:
        logger.error(f"An error occurred during API discovery notification handling: {str(e)}")
        return {'error': str(e)}