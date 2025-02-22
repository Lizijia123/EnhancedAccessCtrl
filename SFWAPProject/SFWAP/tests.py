from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from unittest.mock import patch
from rest_framework.test import APIClient
from .models import TargetApplication, API, LoginCredential
from rest_framework.authtoken.models import Token
import json
from django.utils import timezone

# 获取当前项目使用的用户模型
User = get_user_model()


class TargetApplicationAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.get_target_app_list_url = reverse('get_target_app_list')
        self.target_app_url = reverse('target_app')

    def test_get_target_app_list(self):
        response = self.client.get(self.get_target_app_list_url)
        self.assertEqual(response.status_code, 200)

    def test_create_target_app_success(self):
        data = {
            'APP_name': 'Test App',
            'APP_url': 'https://example.com',
            'user_behavior_cycle': 10,
            'SFWAP_address': '127.0.0.1:8000',
            'description': 'Test description',
            'login_credentials': [
                {
                    'user_role': 'admin',
                    'username': 'admin',
                    'password': 'adminpassword'
                },
                {
                    'user_role': 'user',
                    'username': 'user',
                    'password': 'userpassword'
                }
            ],
            'is_draft': False
        }
        response = self.client.post(self.target_app_url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TargetApplication.objects.count(), 1)

    def test_create_target_app_missing_fields(self):
        data = {
            'APP_name': 'Test App',
            'APP_url': 'https://example.com',
            'user_behavior_cycle': 10,
            'SFWAP_address': '127.0.0.1:8000',
            'description': 'Test description',
            'login_credentials': [
                {
                    'user_role': 'admin',
                    'username': 'admin',
                    'password': 'adminpassword'
                }
            ]
        }
        response = self.client.post(self.target_app_url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 400)


class APIListAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.get_api_lists_url = reverse('get_api_lists')
        self.update_user_api_list_url = reverse('update_user_api_list')
        self.target_app = TargetApplication.objects.create(
            APP_name='Test App',
            APP_url='https://example.com',
            user_behavior_cycle=10,
            SFWAP_address='127.0.0.1:8000',
            description='Test description',
            user=self.user,
            is_draft=False
        )

    def test_get_api_lists(self):
        url = f'{self.get_api_lists_url}?app_id={self.target_app.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    @patch('requests.post')
    def test_update_user_api_list_success(self, mock_post):
        mock_post.return_value.status_code = 200
        api = API.objects.create(
            sample_url='https://example.com/api',
            sample_request_data='{}',
            request_method='GET',
            function_description='Test API',
            permission_info='Test permission'
        )
        data = {
            'user_API_list': [
                {
                    'sample_url': 'https://example.com/api',
                    'sample_request_data': '{}',
                    'request_method': 'GET',
                    'function_description': 'Test API',
                    'permission_info': 'Test permission',
                    'path_segment_list': [],
                    'request_param_list': [],
                    'request_data_fields': []
                }
            ]
        }
        url = f'{self.update_user_api_list_url}?app_id={self.target_app.id}'
        response = self.client.put(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 409)


class APIDiscoveryAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.api_discovery_url = reverse('api_discovery')
        self.finish_api_discovery_url = reverse('finish_api_discovery')
        self.cancel_api_discovery_url = reverse('cancel_api_discovery')
        self.api_discovery_notification_url = reverse('api_discovery_notification')
        self.target_app = TargetApplication.objects.create(
            APP_name='Test App',
            APP_url='https://example.com',
            user_behavior_cycle=10,
            SFWAP_address='127.0.0.1:8000',
            description='Test description',
            user=self.user,
            is_draft=False
        )

    @patch('requests.post')
    def test_api_discovery_auto(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'message': 'API discovery started'}
        url = f'{self.api_discovery_url}?app_id={self.target_app.id}&mode=AUTO'
        response = self.client.get(url)
        print(response.content)
        self.assertEqual(response.status_code, 200)

    @patch('requests.get')
    def test_finish_api_discovery(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = {'discovered_api_list': []}
        url = f'{self.finish_api_discovery_url}?app_id={self.target_app.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 409)

    @patch('requests.get')
    def test_cancel_api_discovery(self, mock_get):
        mock_get.return_value.status_code = 200
        url = f'{self.cancel_api_discovery_url}?app_id={self.target_app.id}'
        response = self.client.get(url)
        print(response.json())
        self.assertEqual(response.status_code, 409)

    @patch('SFWAP.tasks.handle_api_discovery_notification.delay')
    def test_api_discovery_notification(self, mock_delay):
        data = {
            'discovered_API_list': []
        }
        url = f'{self.api_discovery_notification_url}?app_id={self.target_app.id}'
        response = self.client.post(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)


class DetectionFeatureAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.detect_feature_url = reverse('detect_feature')
        self.target_app = TargetApplication.objects.create(
            APP_name='Test App',
            APP_url='https://example.com',
            user_behavior_cycle=10,
            SFWAP_address='127.0.0.1:8000',
            description='Test description',
            user=self.user,
            is_draft=False
        )

    def test_get_detect_feature_list(self):
        url = f'{self.detect_feature_url}?app_id={self.target_app.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_detect_feature_list(self):
        data = {
            'detect_feature_list': [
                {
                    'name': 'Test Feature',
                    'description': 'Test description',
                    'type': 'DetectFeature'
                }
            ]
        }
        url = f'{self.detect_feature_url}?app_id={self.target_app.id}'
        response = self.client.put(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 200)


class ModelConstructionAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.construct_model_url = reverse('construct_model')
        self.target_app = TargetApplication.objects.create(
            APP_name='Test App',
            APP_url='https://example.com',
            user_behavior_cycle=10,
            SFWAP_address='127.0.0.1:8000',
            description='Test description',
            user=self.user,
            is_draft=False
        )

    @patch('requests.post')
    def test_construct_model(self, mock_post):
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'report': 'Test report', 'error_API_list': []}
        url = f'{self.construct_model_url}?app_id={self.target_app.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 409)


class DetectionConfigAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.detection_config_url = reverse('detection_config')
        self.target_app = TargetApplication.objects.create(
            APP_name='Test App',
            APP_url='https://example.com',
            user_behavior_cycle=10,
            SFWAP_address='127.0.0.1:8000',
            description='Test description',
            user=self.user,
            is_draft=False
        )

    def test_get_detection_config(self):
        url = f'{self.detection_config_url}?app_id={self.target_app.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_update_detection_config(self):
        data = {
            'enhanced_detection_enabled': True,
            'combined_data_duration': 3600
        }
        url = f'{self.detection_config_url}?app_id={self.target_app.id}'
        response = self.client.put(url, json.dumps(data), content_type='application/json')
        self.assertEqual(response.status_code, 409)


class DetectionAPITestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        self.start_detection_url = reverse('start_detection')
        self.pause_detection_url = reverse('pause_detection')
        self.get_detection_records_by_combination_url = reverse('get_detection_records_by_combination')
        self.get_detection_records_by_api_url = reverse('get_detection_records_by_api')
        self.target_app = TargetApplication.objects.create(
            APP_name='Test App',
            APP_url='https://example.com',
            user_behavior_cycle=10,
            SFWAP_address='127.0.0.1:8000',
            description='Test description',
            user=self.user,
            is_draft=False
        )

    @patch('requests.post')
    def test_start_detection(self, mock_post):
        mock_post.return_value.status_code = 200
        url = f'{self.start_detection_url}?app_id={self.target_app.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 409)

    @patch('requests.get')
    def test_pause_detection(self, mock_get):
        mock_get.return_value.status_code = 200
        url = f'{self.pause_detection_url}?app_id={self.target_app.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 409)

    @patch('requests.get')
    def test_get_detection_records_by_combination(self, mock_get):
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = []
        url = f'{self.get_detection_records_by_combination_url}?app_id={self.target_app.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_detection_records_by_api(self):
        url = f'{self.get_detection_records_by_api_url}?app_id={self.target_app.id}'
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)


class SFWAPFullFlowTestCase(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='testuser', password='testpassword', email='test@example.com')
        token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')

        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.get_target_app_list_url = reverse('get_target_app_list')
        self.target_app_url = reverse('target_app')
        self.api_discovery_url = reverse('api_discovery')
        self.finish_api_discovery_url = reverse('finish_api_discovery')
        self.update_user_api_list_url = reverse('update_user_api_list')
        self.construct_model_url = reverse('construct_model')
        self.detection_config_url = reverse('detection_config')
        self.start_detection_url = reverse('start_detection')

    def test_full_flow(self):
        # 注册
        register_data = {
            'username': 'newtestuser',
            'password': 'newtestpassword',
            'email': 'newtest@example.com'
        }
        response = self.client.post(self.register_url, register_data)
        self.assertEqual(response.status_code, 201)

        # 登录
        login_data = {
            'username': 'newtestuser',
            'password': 'newtestpassword'
        }
        response = self.client.post(self.login_url, login_data)
        self.assertEqual(response.status_code, 200)

        # 创建目标应用
        target_app_data = {
            'APP_name': 'Test App',
            'APP_url': 'https://example.com',
            'user_behavior_cycle': 10,
            'SFWAP_address': '127.0.0.1:8000',
            'description': 'Test description',
            'login_credentials': [
                {
                    'user_role': 'admin',
                    'username': 'admin',
                    'password': 'adminpassword'
                },
                {
                    'user_role': 'user',
                    'username': 'user',
                    'password': 'userpassword'
                }
            ],
            'is_draft': False
        }
        response = self.client.post(self.target_app_url, json.dumps(target_app_data), content_type='application/json')
        self.assertEqual(response.status_code, 200)
        target_app = TargetApplication.objects.first()

        # 自动 API 发现
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {'message': 'API discovery started'}
            auto_api_discovery_url = f'{self.api_discovery_url}?app_id={target_app.id}&mode=AUTO'
            response = self.client.get(auto_api_discovery_url)
            self.assertEqual(response.status_code, 200)

        target_app = TargetApplication.objects.first()
        target_app.last_API_discovery_at = timezone.now()
        target_app.detect_state = 'API_LIST_TO_IMPROVE'
        target_app.save()

        # 手动 API 发现
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {'message': 'Manual API discovery started'}
            manual_api_discovery_url = f'{self.api_discovery_url}?app_id={target_app.id}&mode=MANUAL'
            response = self.client.get(manual_api_discovery_url)
            self.assertEqual(response.status_code, 200)

        # 完成 API 发现
        with patch('requests.get') as mock_get:
            mock_get.return_value.status_code = 200
            mock_get.return_value.json.return_value = {'discovered_api_list': []}
            finish_api_discovery_url = f'{self.finish_api_discovery_url}?app_id={target_app.id}'
            response = self.client.get(finish_api_discovery_url)
            print(response.json())
            self.assertEqual(response.status_code, 200)


        # 编辑 API 列表
        api = API.objects.create(
            sample_url='https://example.com/api',
            sample_request_data='{}',
            request_method='GET',
            function_description='Test API',
            permission_info='Test permission'
        )
        user_api_list_data = {
            'user_API_list': [
                {
                    'sample_url': 'https://example.com/api',
                    'sample_request_data': '{}',
                    'request_method': 'GET',
                    'function_description': 'Test API',
                    'permission_info': 'Test permission',
                    'path_segment_list': [],
                    'request_param_list': [],
                    'request_data_fields': []
                }
            ]
        }
        update_user_api_list_url = f'{self.update_user_api_list_url}?app_id={target_app.id}'
        with patch('requests.post') as mock_post:  # 模拟向 SFWAP_address 的请求
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {'message': 'User API list updated successfully'}
            response = self.client.put(update_user_api_list_url, json.dumps(user_api_list_data),
                                       content_type='application/json')
            self.assertEqual(response.status_code, 200)

        # 模型构建
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            mock_post.return_value.json.return_value = {'report': 'Test report', 'error_API_list': []}
            construct_model_url = f'{self.construct_model_url}?app_id={target_app.id}'
            response = self.client.get(construct_model_url)
            self.assertEqual(response.status_code, 200)

        # 编辑检测配置
        detection_config_data = {
            'enhanced_detection_enabled': True,
            'combined_data_duration': 3600
        }
        detection_config_url = f'{self.detection_config_url}?app_id={target_app.id}'
        response = self.client.put(detection_config_url, json.dumps(detection_config_data),
                                   content_type='application/json')
        print(response.json())
        self.assertEqual(response.status_code, 200)

        # 启动检测
        with patch('requests.post') as mock_post:
            mock_post.return_value.status_code = 200
            start_detection_url = f'{self.start_detection_url}?app_id={target_app.id}'
            response = self.client.get(start_detection_url)
            self.assertEqual(response.status_code, 200)