from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from .models import User, LoginCredential, TargetApplication
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from .models import User, LoginCredential, TargetApplication, API, PathSegment, RequestParam, RequestDataField
import json
from unittest.mock import patch

class UserRegistrationLoginLogoutTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.register_url = reverse('register')
        self.login_url = reverse('login')
        self.logout_url = reverse('logout')
        self.target_app_url = reverse('target_app')

    def test_user_registration(self):
        data = {
            'username': 'test',
            'password': 'password',
            'email': 'test@example.com'
        }
        response = self.client.post(self.register_url, data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual(User.objects.count(), 1)

    def test_user_login(self):
        user = User.objects.create_user(username='test', password='password', email='test@example.com')
        data = {
            'username': 'test',
            'password': 'password'
        }
        response = self.client.post(self.login_url, data)
        self.assertEqual(response.status_code, 200)

    def test_user_logout(self):
        user = User.objects.create_user(username='test', password='password', email='test@example.com')
        token = Token.objects.create(user=user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {token.key}')
        response = self.client.post(self.logout_url)
        self.assertEqual(response.status_code, 200)


class TargetApplicationCreateGetTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(username='test', password='password', email='test@example.com')
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.target_app_url = reverse('target_app')

    def test_create_target_application_non_draft(self):
        data = {
            "APP_name": "TestApp",
            "APP_url": "https://example.com",
            "user_behavior_cycle": 50,
            "SFWAP_address": "127.0.0.1:8000",
            "description": "This is a test application",
            "login_credentials": [
                {
                    "user_role": "admin",
                    "username": "adminuser",
                    "password": "adminpass"
                },
                {
                    "user_role": "guest",
                    "username": "guestuser",
                    "password": "guestpass"
                }
            ],
            "is_draft": False
        }
        response = self.client.post(self.target_app_url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TargetApplication.objects.count(), 1)
        self.assertEqual(TargetApplication.objects.first().is_draft, False)

    def test_create_target_application_draft(self):
        data = {
            "APP_name": "TestAppDraft",
            "APP_url": "https://example.com",
            "user_behavior_cycle": 50,
            "SFWAP_address": "127.0.0.1:8000",
            "description": "This is a test draft application",
            "login_credentials": [
                {
                    "user_role": "admin",
                    "username": "adminuser",
                    "password": "adminpass"
                },
                {
                    "user_role": "guest",
                    "username": "guestuser",
                    "password": "guestpass"
                }
            ],
            "is_draft": True
        }
        response = self.client.post(self.target_app_url, data, format='json')
        self.assertEqual(response.status_code, 201)
        self.assertEqual(TargetApplication.objects.count(), 1)
        self.assertEqual(TargetApplication.objects.first().is_draft, True)

    def test_create_target_application_invalid_app_name(self):
        data = {
            "APP_name": "a" * 21,
            "APP_url": "https://example.com",
            "user_behavior_cycle": 50,
            "SFWAP_address": "127.0.0.1:8000",
            "description": "This is a test application",
            "login_credentials": [
                {
                    "user_role": "admin",
                    "username": "adminuser",
                    "password": "adminpass"
                },
                {
                    "user_role": "guest",
                    "username": "guestuser",
                    "password": "guestpass"
                }
            ],
            "is_draft": False
        }
        response = self.client.post(self.target_app_url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_target_application_invalid_app_url(self):
        data = {
            "APP_name": "TestApp",
            "APP_url": "invalid_url",
            "user_behavior_cycle": 50,
            "SFWAP_address": "127.0.0.1:8000",
            "description": "This is a test application",
            "login_credentials": [
                {
                    "user_role": "admin",
                    "username": "adminuser",
                    "password": "adminpass"
                },
                {
                    "user_role": "guest",
                    "username": "guestuser",
                    "password": "guestpass"
                }
            ],
            "is_draft": False
        }
        response = self.client.post(self.target_app_url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_target_application_invalid_user_behavior_cycle(self):
        data = {
            "APP_name": "TestApp",
            "APP_url": "https://example.com",
            "user_behavior_cycle": 101,
            "SFWAP_address": "127.0.0.1:8000",
            "description": "This is a test application",
            "login_credentials": [
                {
                    "user_role": "admin",
                    "username": "adminuser",
                    "password": "adminpass"
                },
                {
                    "user_role": "guest",
                    "username": "guestuser",
                    "password": "guestpass"
                }
            ],
            "is_draft": False
        }
        response = self.client.post(self.target_app_url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_target_application_invalid_sfwap_address(self):
        data = {
            "APP_name": "TestApp",
            "APP_url": "https://example.com",
            "user_behavior_cycle": 50,
            "SFWAP_address": "invalid_address",
            "description": "This is a test application",
            "login_credentials": [
                {
                    "user_role": "admin",
                    "username": "adminuser",
                    "password": "adminpass"
                },
                {
                    "user_role": "guest",
                    "username": "guestuser",
                    "password": "guestpass"
                }
            ],
            "is_draft": False
        }
        response = self.client.post(self.target_app_url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_create_target_application_insufficient_login_credentials(self):
        data = {
            "APP_name": "TestApp",
            "APP_url": "https://example.com",
            "user_behavior_cycle": 50,
            "SFWAP_address": "127.0.0.1:8000",
            "description": "This is a test application",
            "login_credentials": [
                {
                    "user_role": "admin",
                    "username": "adminuser",
                    "password": "adminpass"
                }
            ],
            "is_draft": False
        }
        response = self.client.post(self.target_app_url, data, format='json')
        self.assertEqual(response.status_code, 400)

    def test_get_target_application(self):
        target_app = TargetApplication.objects.create(
            APP_name="TestApp",
            APP_url="https://example.com",
            user_behavior_cycle=50,
            SFWAP_address="127.0.0.1:8000",
            description="This is a test application",
            user=self.user,
            is_draft=False
        )
        credential1 = LoginCredential.objects.create(user_role="admin", username="adminuser", password="adminpass")
        credential2 = LoginCredential.objects.create(user_role="guest", username="guestuser", password="guestpass")
        target_app.login_credentials.add(credential1, credential2)

        response = self.client.get(f'{self.target_app_url}?id={target_app.id}')
        self.assertEqual(response.status_code, 200)


class TargetApplicationUpdateDeleteTests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            password='testpassword',
            email='test@example.com'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')
        self.target_app_url = reverse('target_app')

        # 创建非暂存目标应用
        self.non_draft_app = TargetApplication.objects.create(
            APP_name="NonDraftApp",
            APP_url="https://nondraft.com",
            user_behavior_cycle=50,
            SFWAP_address="127.0.0.1:8000",
            description="Non-draft test application",
            user=self.user,
            is_draft=False
        )
        cred1 = LoginCredential.objects.create(
            user_role="admin",
            username="adminuser",
            password="adminpass"
        )
        cred2 = LoginCredential.objects.create(
            user_role="guest",
            username="guestuser",
            password="guestpass"
        )
        self.non_draft_app.login_credentials.add(cred1, cred2)

        # 创建暂存目标应用
        self.draft_app = TargetApplication.objects.create(
            APP_name="DraftApp",
            APP_url="https://draft.com",
            user_behavior_cycle=50,
            SFWAP_address="127.0.0.1:8000",
            description="Draft test application",
            user=self.user,
            is_draft=True
        )
        self.draft_app.login_credentials.add(cred1, cred2)

    def test_update_non_draft_app_valid(self):
        """测试更新非暂存目标应用的有效属性"""
        data = {
            "APP_url": "https://newnondraft.com",
            "description": "Updated non-draft description"
        }
        response = self.client.put(
            f'{self.target_app_url}?id={self.non_draft_app.id}',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.non_draft_app.refresh_from_db()
        self.assertEqual(self.non_draft_app.APP_url, "https://newnondraft.com")
        self.assertEqual(self.non_draft_app.description, "Updated non-draft description")

    def test_update_draft_app_valid(self):
        """测试更新暂存目标应用的有效属性"""
        data = {
            "APP_url": "https://newdraft.com",
            "description": "Updated draft description"
        }
        response = self.client.put(
            f'{self.target_app_url}?id={self.draft_app.id}',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, 200)
        self.draft_app.refresh_from_db()
        self.assertEqual(self.draft_app.APP_url, "https://newdraft.com")
        self.assertEqual(self.draft_app.description, "Updated draft description")

    def test_update_app_invalid_app_name(self):
        """测试更新目标应用时使用无效的 APP_name"""
        data = {
            "APP_name": "a" * 21
        }
        response = self.client.put(
            f'{self.target_app_url}?id={self.non_draft_app.id}',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_update_app_invalid_app_url(self):
        """测试更新目标应用时使用无效的 APP_url"""
        data = {
            "APP_url": "invalid_url"
        }
        response = self.client.put(
            f'{self.target_app_url}?id={self.non_draft_app.id}',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_update_app_invalid_user_behavior_cycle(self):
        """测试更新目标应用时使用无效的 user_behavior_cycle"""
        data = {
            "user_behavior_cycle": 101
        }
        response = self.client.put(
            f'{self.target_app_url}?id={self.non_draft_app.id}',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_update_app_invalid_sfwap_address(self):
        """测试更新目标应用时使用无效的 SFWAP_address"""
        data = {
            "SFWAP_address": "invalid_address"
        }
        response = self.client.put(
            f'{self.target_app_url}?id={self.non_draft_app.id}',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_update_app_try_to_set_draft_true(self):
        """测试更新目标应用时尝试将其设置为暂存状态（不允许）"""
        data = {
            "is_draft": True
        }
        response = self.client.put(
            f'{self.target_app_url}?id={self.non_draft_app.id}',
            data,
            format='json'
        )
        self.assertEqual(response.status_code, 400)

    def test_delete_non_draft_app(self):
        """测试删除非暂存目标应用"""
        response = self.client.delete(
            f'{self.target_app_url}?id={self.non_draft_app.id}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TargetApplication.objects.filter(id=self.non_draft_app.id).count(), 0)

    def test_delete_draft_app(self):
        """测试删除暂存目标应用"""
        response = self.client.delete(
            f'{self.target_app_url}?id={self.draft_app.id}'
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(TargetApplication.objects.filter(id=self.draft_app.id).count(), 0)

    def test_delete_app_missing_id(self):
        """测试删除目标应用时缺少 ID"""
        response = self.client.delete(self.target_app_url)
        self.assertEqual(response.status_code, 400)



class APITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='test',
            password='password',
            email='test@example.com'
        )
        self.token = Token.objects.create(user=self.user)
        self.client.credentials(HTTP_AUTHORIZATION=f'Token {self.token.key}')

        self.target_app = TargetApplication.objects.create(
            APP_name="TestApp",
            APP_url="https://testapp.com",
            user_behavior_cycle=50,
            SFWAP_address="127.0.0.1:8000",
            description="Test application",
            user=self.user,
            is_draft=False
        )
        self.credential = LoginCredential.objects.create(
            user_role="admin",
            username="adminuser",
            password="adminpass"
        )
        self.target_app.login_credentials.add(self.credential)

        # 创建 API 数据
        self.api = API.objects.create(
            sample_url="https://testapi.com",
            sample_request_data="{}",
            request_method="GET",
            function_description="Test API",
            permission_info="Test permission"
        )
        self.segment = PathSegment.objects.create(
            name="test_segment",
            is_path_variable=False
        )
        self.param = RequestParam.objects.create(
            name="test_param",
            is_necessary=True
        )
        self.field = RequestDataField.objects.create(
            name="test_field",
            type="String"
        )
        self.api.path_segment_list.add(self.segment)
        self.api.request_param_list.add(self.param)
        self.api.request_data_fields.add(self.field)
        self.target_app.discovered_API_list.add(self.api)
        self.target_app.user_API_list.add(self.api)

    def test_get_api_lists(self):
        url = reverse('get_api_lists')
        response = self.client.get(url, {'id': self.target_app.id})
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertIn('discovered_API_list', data)
        self.assertIn('user_API_list', data)

    def test_update_user_api_list(self):
        url = reverse('update_user_api_list')
        api_data = {
            "sample_url": "https://newtestapi.com",
            "sample_request_data": "{}",
            "request_method": "POST",
            "function_description": "New Test API",
            "permission_info": "New Test permission",
            "path_segment_list": [
                {
                    "name": "new_test_segment",
                    "is_path_variable": True
                }
            ],
            "request_param_list": [
                {
                    "name": "new_test_param",
                    "is_necessary": False
                }
            ],
            "request_data_fields": [
                {
                    "name": "new_test_field",
                    "type": "Number"
                }
            ]
        }
        data = {
            "user_API_list": [api_data]
        }
        # 将 id 作为查询参数添加到 URL 中
        full_url = f"{url}?id={self.target_app.id}"
        response = self.client.put(full_url, data, format='json')
        self.assertEqual(response.status_code, 200)
        self.target_app.refresh_from_db()
        self.assertEqual(self.target_app.user_API_list.count(), 1)

    @patch('requests.get')
    def test_api_discovery(self, mock_get):
        mock_response = mock_get.return_value
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "discovered_API_list": [
                {
                    "sample_url": "https://discoveredapi.com",
                    "sample_request_data": "{}",
                    "request_method": "PUT",
                    "function_description": "Discovered Test API",
                    "permission_info": "Discovered Test permission",
                    "path_segment_list": [
                        {
                            "name": "discovered_test_segment",
                            "is_path_variable": True
                        }
                    ],
                    "request_param_list": [
                        {
                            "name": "discovered_test_param",
                            "is_necessary": False
                        }
                    ],
                    "request_data_fields": [
                        {
                            "name": "discovered_test_field",
                            "type": "List"
                        }
                    ]
                }
            ]
        }
        url = reverse('api_discovery')
        response = self.client.get(url, {'id': self.target_app.id})
        self.assertEqual(response.status_code, 200)
        self.target_app.refresh_from_db()
        self.assertEqual(self.target_app.discovered_API_list.count(), 1)
