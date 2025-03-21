# views.py
from typing import List, Dict
import logging
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
from django.db import transaction

from .models import *
from django.views.decorators.csrf import csrf_exempt
import json
import requests
from django.http import JsonResponse
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from .models import TargetApplication, API, PathSegment, RequestParam, RequestDataField
from django.core.exceptions import ValidationError

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.permissions import IsAuthenticated
from rest_framework.authentication import TokenAuthentication
from rest_framework.response import Response
# from django.contrib.auth.models import User
logger = logging.getLogger(__name__)

@api_view(['GET'])
@authentication_classes([TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_user_info(request):
    user = request.user
    user_info = {
        'id': user.id,
        'username': user.username,
        'email': user.email
    }
    return Response(user_info)

from django.contrib.auth import get_user_model
User = get_user_model()

@csrf_exempt
def register(request):
    if request.method == 'POST':

        username = json.loads(request.body).get('username')
        password = json.loads(request.body).get('password')
        email = json.loads(request.body).get('email')

        if not username or not password or not email:
            return JsonResponse({
                'code': 400,
                'error': 'Missing required fields'
            }, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({
                'code': 400,
                'error': 'Username already exists'
            }, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({
                'code': 400,
                'error': 'Email already exists'
            }, status=400)

        hashed_password = make_password(password)
        user = User(username=username, email=email, password=hashed_password)
        user.save()

        return JsonResponse({
            'code': 201,
            'message': 'User registered successfully'
        }, status=201)

    return JsonResponse({
        'code': 405,
        'error': 'Invalid request method'
    }, status=405)


@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        username = json.loads(request.body).get('username')
        password = json.loads(request.body).get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({
                'code': 200,
                'message': 'User logged in successfully'
            }, status=200)
        else:
            return JsonResponse({
                'code': 401,
                'error': 'Invalid username or password'
            }, status=401)

    return JsonResponse({
        'code': 405,
        'error': 'Invalid request method'
    }, status=405)


from rest_framework.authtoken.models import Token

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def user_logout(request):
    if request.method == 'POST':
        token = Token.objects.get(user=request.user)
        token.delete()
        logout(request)
        return JsonResponse({
            'code': 200,
            'message': 'User logged out successfully'
        }, status=200)

    return JsonResponse({
        'code': 405,
        'error': 'Invalid request method'
    }, status=405)


def target_app_model_to_view(target_app):
    login_credentials = []
    for credential in target_app.login_credentials.all():
        login_credentials.append({
            'user_role': credential.user_role,
            'username': credential.username,
            'password': credential.password
        })

    return {
        'id': target_app.id,
        'APP_name': target_app.APP_name,
        'APP_url': target_app.APP_url,
        'user_behavior_cycle': target_app.user_behavior_cycle,
        'SFWAP_address': target_app.SFWAP_address,
        'description': target_app.description,
        'created_at': target_app.created_at.strftime('%Y-%m-%d %H:%M:%S') if target_app.created_at else None,
        'updated_at': target_app.updated_at.strftime('%Y-%m-%d %H:%M:%S') if target_app.updated_at else None,
        'is_draft': target_app.is_draft,
        'last_API_discovery_at': target_app.last_API_discovery_at.strftime(
            '%Y-%m-%d %H:%M:%S') if target_app.last_API_discovery_at else None,
        'last_model_construction_at': target_app.last_model_construction_at.strftime(
            '%Y-%m-%d %H:%M:%S') if target_app.last_model_construction_at else None,
        'login_credentials': login_credentials,
        'detect_state': target_app.detect_state,
        'model_report': compile_report(target_app.model_report),
        'enhanced_detection_enabled': target_app.enhanced_detection_enabled,
        'combined_data_duration': target_app.combined_data_duration
    }


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_target_app_list(request):
    try:
        user = request.user
        target_apps = TargetApplication.objects.filter(user=user)
        target_apps_info = []
        for target_app in target_apps:
            target_apps_info.append(target_app_model_to_view(target_app))
        return JsonResponse({
            'code': 200,
            'data': {
                'target_app_list': target_apps_info,
                'total': len(target_apps_info)
            }
        }, safe=False, status=200)
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'error': str(e)
        }, status=500)

from rest_framework.pagination import PageNumberPagination
from django.core.paginator import Paginator, EmptyPage
class CustomPagination(PageNumberPagination):
    page_size = 10  # 每页显示的记录数
    page_size_query_param = 'page_size'  # 允许客户端通过该参数指定每页记录数
    max_page_size = 100  # 最大每页记录数

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_target_app_list_pagely(request):
    try:
        user = request.user
        target_apps = TargetApplication.objects.filter(user=user).order_by('-created_at')

        # 创建分页器实例
        paginator = CustomPagination()
        # 对查询集进行分页
        page = paginator.paginate_queryset(target_apps, request)

        return JsonResponse({
            'code': 200,
            'data': {
                'traffic_data_list': [target_app_model_to_view(target_app) 
                                    for target_app in (page if page else target_apps)],
                'total': paginator.page.paginator.count if page else len(target_apps),
                'next': paginator.get_next_link() if page else None,
                'previous': paginator.get_previous_link() if page else None
            }
        }, safe=False, status=200)
    
    except EmptyPage as e:
        return JsonResponse({
            'code': 400,
            'error': str(e)
        }, status=400)





def setup_basic_features(target_app):
    target_app.detect_feature_list.clear()
    get_basic_feature_url = f'http://{target_app.SFWAP_address}/basic_features'
    try:
        response = requests.get(get_basic_feature_url)
        result = response.json()

        for feature in target_app.detect_feature_list.all():
            feature.delete()
        target_app.detect_feature_list.clear()


        basic_feature_list = result.get('basic_feature_list')
        for basic_feature_info in basic_feature_list:
            feature, created = DetectFeature.objects.get_or_create(
                name=basic_feature_info['name'],
                defaults={'description': basic_feature_info['description']}
            )
            target_app.detect_feature_list.add(feature)
        return None
    except requests.RequestException as e:
        return JsonResponse({
            'code': 500,
            'error': f'Error making get basic feature list request: {str(e)}'
        }, status=500)
    except ValueError:
        return JsonResponse({
            'code': 500,
            'error': 'Invalid JSON response from getting basic feature list'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'error': str(e)
        }, status=500)


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def target_app(request):
    if request.method == 'GET':
        app_id = request.query_params.get('id')
        if not app_id:
            return JsonResponse({
                'code': 400,
                'error': 'Missing target application ID'
            }, status=400)
        try:
            target_app = TargetApplication.objects.get(id=app_id, user=request.user)
            # setup_basic_features(target_app)
            return JsonResponse({
                'code': 200,
                'data': target_app_model_to_view(target_app)
            }, status=200)
        except TargetApplication.DoesNotExist:
            return JsonResponse({
                'code': 404,
                'error': 'Target application not found or you do not have permission'
            }, status=404)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            APP_name = data.get('APP_name')
            APP_url = data.get('APP_url')
            user_behavior_cycle = data.get('user_behavior_cycle')
            SFWAP_address = data.get('SFWAP_address')
            description = data.get('description')
            login_credentials_data = data.get('login_credentials', [])
            is_draft = data.get('is_draft')
            if not all([APP_name, APP_url, user_behavior_cycle, SFWAP_address, description,
                        len(login_credentials_data) >= 2]):
                return JsonResponse({
                    'code': 400,
                    'error': 'Missing required fields or insufficient login credentials'
                }, status=400)
            if TargetApplication.objects.filter(APP_name=APP_name).exists():
                return JsonResponse({
                    'code': 400,
                    'error': 'APP_name already exists'
                }, status=400)

            detect_state = 'BASIC_INFO_TO_CONFIGURE' if is_draft else 'API_LIST_TO_DISCOVER'

            target_app = TargetApplication(
                APP_name=APP_name,
                APP_url=APP_url,
                user_behavior_cycle=user_behavior_cycle,
                SFWAP_address=SFWAP_address,
                description=description,
                user=request.user,
                is_draft=is_draft,
                detect_state=detect_state
            )
            try:
                target_app.full_clean()
            except ValidationError as e:
                return JsonResponse({
                    'code': 400,
                    'error': str(e)
                }, status=400)

            valid_credentials = []
            for credential_data in login_credentials_data:
                user_role = credential_data.get('user_role')
                username = credential_data.get('username')
                password = credential_data.get('password')
                if not all([user_role, username, password]):
                    return JsonResponse({
                        'code': 400,
                        'error': 'Missing fields in login credential'
                    }, status=400)
                credential = LoginCredential(
                    user_role=user_role,
                    username=username,
                    password=password
                )
                try:
                    credential.full_clean()
                    valid_credentials.append(credential)
                except ValidationError as e:
                    return JsonResponse({
                        'code': 400,
                        'error': f'Invalid login credential data: {str(e)}'
                    }, status=400)

            target_app.save()
            for credential in valid_credentials:
                credential.save()
                target_app.login_credentials.add(credential)

            basic_feature_setup_res = setup_basic_features(target_app)
            if basic_feature_setup_res is not None:
                return basic_feature_setup_res

            return JsonResponse({
                'code': 200,
                'message': 'Target application created successfully',
                'data': target_app_model_to_view(target_app)
            }, status=200)

        except ValidationError as e:
            return JsonResponse({
                'code': 400,
                'error': str(e)
            }, status=400)
        except json.JSONDecodeError:
            return JsonResponse({
                'code': 400,
                'error': 'Invalid JSON data'
            }, status=400)

    elif request.method == 'PUT':
        try:
            app_id = request.query_params.get('id')
            if not app_id:
                return JsonResponse({
                    'code': 400,
                    'error': 'Missing target application ID'
                }, status=400)
            try:
                target_app = TargetApplication.objects.get(id=app_id, user=request.user)
            except TargetApplication.DoesNotExist:
                return JsonResponse({
                    'code': 404,
                    'error': 'Target application not found or you do not have permission'
                }, status=404)

            data = json.loads(request.body)
            APP_name = data.get('APP_name', target_app.APP_name)
            APP_url = data.get('APP_url', target_app.APP_url)
            user_behavior_cycle = data.get('user_behavior_cycle', target_app.user_behavior_cycle)
            SFWAP_address = data.get('SFWAP_address', target_app.SFWAP_address)
            description = data.get('description', target_app.description)
            login_credentials_data = data.get('login_credentials')

            if TargetApplication.objects.filter(APP_name=APP_name).exclude(id=app_id).exists():
                return JsonResponse({
                    'code': 400,
                    'error': 'APP_name already exists'
                }, status=400)
            if not login_credentials_data or len(login_credentials_data) < 2:
                return JsonResponse({
                    'code': 400,
                    'error': 'Insufficient login credentials'
                }, status=400)

            target_app.APP_name = APP_name
            target_app.APP_url = APP_url
            target_app.user_behavior_cycle = user_behavior_cycle
            target_app.SFWAP_address = SFWAP_address
            target_app.description = description

            try:
                target_app.full_clean()
            except ValidationError as e:
                return JsonResponse({
                    'code': 400,
                    'error': str(e)
                }, status=400)

            valid_credentials = []
            for credential_data in login_credentials_data:
                user_role = credential_data.get('user_role')
                username = credential_data.get('username')
                password = credential_data.get('password')
                if not all([user_role, username, password]):
                    return JsonResponse({
                        'code': 400,
                        'error': 'Missing fields in login credential'
                    }, status=400)

                credential = LoginCredential(
                    user_role=user_role,
                    username=username,
                    password=password
                )
                try:
                    credential.full_clean()
                    valid_credentials.append(credential)
                except ValidationError as e:
                    return JsonResponse({
                        'code': 400,
                        'error': f'Invalid login credential data: {str(e)}'
                    }, status=400)

            target_app.login_credentials.all().delete()
            target_app.save()
            for credential in valid_credentials:
                credential.save()
                target_app.login_credentials.add(credential)

            setup_basic_features(target_app)

            return JsonResponse({
                'code': 200,
                'message': 'Target application updated successfully',
                'data': target_app_model_to_view(target_app)
            }, status=200)
        except ValidationError as e:
            return JsonResponse({
                'code': 400,
                'error': str(e)
            }, status=400)
        except json.JSONDecodeError:
            return JsonResponse({
                'code': 400,
                'error': 'Invalid JSON data'
            }, status=400)

    elif request.method == 'DELETE':
        app_id = request.query_params.get('id')
        if not app_id:
            return JsonResponse({
                'code': 400,
                'error': 'Missing target application ID'
            }, status=400)

        try:
            target_app = TargetApplication.objects.get(id=app_id, user=request.user)
            target_app.delete()
            return JsonResponse({
                'code': 200,
                'message': 'Target application deleted successfully'
            }, status=200)
        except TargetApplication.DoesNotExist:
            return JsonResponse({
                'code': 404,
                'error': 'Target application not found or you do not have permission'
            }, status=404)

    return JsonResponse({
        'code': 405,
        'error': 'Invalid request method'
    }, status=405)





def API_list_model_to_view(api_list_field):
    API_list = []
    # 判断 api_list_field 是否为查询集
    if hasattr(api_list_field, 'all'):
        api_list = api_list_field.all()
    else:
        api_list = api_list_field
    for api in api_list:
        path_segment_list = []
        for segment in api.path_segment_list.all():
            path_segment_list.append({
                'name': segment.name,
                'is_path_variable': segment.is_path_variable
            })
        request_param_list = []
        for param in api.request_param_list.all():
            request_param_list.append({
                'name': param.name,
                'is_necessary': param.is_necessary
            })
        request_data_fields = []
        for field in api.request_data_fields.all():
            request_data_fields.append({
                'name': field.name,
                'type': field.type
            })
        api_info = {
            'id': api.id,
            'sample_url': api.sample_url,
            'sample_request_data': api.sample_request_data,
            'request_method': api.request_method,
            'function_description': api.function_description,
            'permission_info': api.permission_info,
            'path_segment_list': path_segment_list,
            'request_param_list': request_param_list,
            'request_data_fields': request_data_fields,
            'role_list': api.role_list
        }
        API_list.append(api_info)
    return API_list

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_api_lists(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
        discovered_API_list = API_list_model_to_view(target_app.discovered_API_list)
        user_API_list = API_list_model_to_view(target_app.user_API_list)
        return JsonResponse({
            'code': 200,
            'data':{
                'discovered_API_list': discovered_API_list,
                'discovered_API_list_total': len(discovered_API_list),
                'user_API_list': user_API_list,
                'user_API_list_total': len(user_API_list)
            }
        }, status=200)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)

class APIPagination(PageNumberPagination):
    page_size = 10  # 每页显示的记录数
    page_size_query_param = 'page_size'  # 允许客户端通过该参数指定每页记录数
    max_page_size = 100  # 最大每页记录数

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_api_lists_pagely(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)

        # 初始化分页器
        DALpaginator = APIPagination()
        UALpaginator = APIPagination()

        # 对 discovered_API_list 进行分页
        discovered_api_list_page = DALpaginator.paginate_queryset(target_app.discovered_API_list.all().order_by('id'), request)
        discovered_API_list = API_list_model_to_view(discovered_api_list_page)

        # 对 user_API_list 进行分页
        user_api_list_page = UALpaginator.paginate_queryset(target_app.user_API_list.all().order_by('id'), request)
        user_API_list = API_list_model_to_view(user_api_list_page)

        return JsonResponse({
            'code': 200,
            'data': {
                'discovered_API_list': discovered_API_list,
                'discovered_API_list_total': DALpaginator.page.paginator.count if discovered_api_list_page else len(discovered_API_list),
                'discovered_API_list_next': DALpaginator.get_next_link() if discovered_api_list_page else None,
                'discovered_API_list_previous': DALpaginator.get_previous_link() if discovered_api_list_page else None,
                'user_API_list': user_API_list,
                'user_API_list_total': UALpaginator.page.paginator.count if user_api_list_page else len(user_API_list),
                'user_API_list_next': UALpaginator.get_next_link() if user_api_list_page else None,
                'user_API_list_previous': UALpaginator.get_previous_link() if user_api_list_page else None
            }
        }, status=200)
    except EmptyPage as e:
        return JsonResponse({
            'code': 404,
            'error': str(e)
        }, status=404)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)






def validate_api(api_data):
    function_description = api_data.get('function_description')
    permission_info = api_data.get('permission_info')
    if not function_description or not permission_info:
        return JsonResponse({
            'code': 400,
            'error': 'Each API must have non - empty function_description and permission_info'
        }, status=400)

    sample_url = api_data.get('sample_url')
    sample_request_data = api_data.get('sample_request_data')
    request_method = api_data.get('request_method')
    role_list = api_data.get('role_list')
    if not role_list:
        role_list = []

    api = API(
        sample_url=sample_url,
        sample_request_data=sample_request_data,
        request_method=request_method,
        function_description=function_description,
        permission_info=permission_info,
        role_list=role_list
    )
    try:
        api.full_clean()
    except ValidationError as e:
        return JsonResponse({
            'code': 400,
            'error': f'Invalid API data: {str(e)}'
        }, status=400)

    path_segment_list_data = api_data.get('path_segment_list', [])
    path_segments = []
    for segment_data in path_segment_list_data:
        name = segment_data.get('name')
        is_path_variable = segment_data.get('is_path_variable')
        if not name or is_path_variable is None:
            return JsonResponse({
                'code': 400,
                'error': 'Each path segment must have a non - empty name and a valid is_path_variable value'
            }, status=400)
        segment = PathSegment(name=name, is_path_variable=is_path_variable)
        try:
            segment.full_clean()
            path_segments.append(segment)
        except ValidationError as e:
            return JsonResponse({
                'code': 400,
                'error': f'Invalid path segment data: {str(e)}'
            }, status=400)

    request_param_list_data = api_data.get('request_param_list', [])
    request_params = []
    for param_data in request_param_list_data:
        name = param_data.get('name')
        is_necessary = param_data.get('is_necessary')
        if not name or is_necessary is None:
            return JsonResponse({
                'code': 400,
                'error': 'Each request param must have a non - empty name and a valid is_necessary value'
            }, status=400)
        param = RequestParam(name=name, is_necessary=is_necessary)
        try:
            param.full_clean()
            request_params.append(param)
        except ValidationError as e:
            return JsonResponse({
                'code': 400,
                'error': f'Invalid request param data: {str(e)}'
            }, status=400)

    request_data_fields_data = api_data.get('request_data_fields', [])
    request_data_fields = []
    for field_data in request_data_fields_data:
        name = field_data.get('name')
        type_ = field_data.get('type')
        if not name or not type_ or type_ not in ['String', 'Number', 'Boolean', 'List', 'Object']:
            return JsonResponse({
                'code': 400,
                'error': 'Each request data field must have a non - empty name and a valid type (String, Number, Boolean, List, Object)'
            }, status=400)
        field = RequestDataField(name=name, type=type_)
        try:
            field.full_clean()
            request_data_fields.append(field)
        except ValidationError as e:
            return JsonResponse({
                'code': 400,
                'error': f'Invalid request data field data: {str(e)}'
            }, status=400)

    # 不直接设置多对多关系，将关联对象存储在字典中
    return {
        'api': api,
        'path_segments': path_segments,
        'request_params': request_params,
        'request_data_fields': request_data_fields
    }


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_api_list_v1(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)
    if target_app.last_API_discovery_at is None:
        return JsonResponse({
            'code': 409,
            'error': 'The target application has never had API discovery'
        }, status=409)
    if target_app.detect_state == 'STARTED':
        return JsonResponse({
            'code': 409,
            'error': 'You cannot update the API list during detection'
        }, status=409)

    try:
        data = json.loads(request.body)
        user_api_list_data = data.get('user_API_list', [])
        api_id_list = []
        new_api_id_list = []
        valid_api_items: List[Dict] = []
        for api_data in user_api_list_data:
            result = validate_api(api_data)
            if isinstance(result, JsonResponse):
                return result
            valid_api_items.append(result)
            api_id_list.append(api_data.get('id'))

        with transaction.atomic():
            for api in target_app.user_API_list.all():
                api.path_segment_list.all().delete()
                api.request_param_list.all().delete()
                api.request_data_fields.all().delete()
                api.delete()
            target_app.user_API_list.clear()

            for valid_api_item in valid_api_items:
                valid_api_item['api'].save()
                new_api_id_list.append(valid_api_item['api'].id)
                for segment in valid_api_item['path_segments']:
                    segment.save()
                for param in valid_api_item['request_params']:
                    param.save()
                for field in valid_api_item['request_data_fields']:
                    field.save()
                valid_api_item['api'].path_segment_list.set(valid_api_item['path_segments'])
                valid_api_item['api'].request_param_list.set(valid_api_item['request_params'])
                valid_api_item['api'].request_data_fields.set(valid_api_item['request_data_fields'])
                target_app.user_API_list.add(valid_api_item['api'])
        
        id_map = {str(api_id_list[i]):str(new_api_id_list[i]) for i in range(len(api_id_list))}

        print(id_map)


        revised_API_seqs = {
            'normal_seqs': [],
            'malicious_seqs': []
        }
        example_API_seqs = data.get('example_API_seqs')
        if example_API_seqs:
            for seq in example_API_seqs['normal_seqs']:
                api_items = []
                for seq_item in seq["seq"]:
                    api_str = f"API_{id_map[str(seq_item['id'])]}({seq_item['description']})"
                    api_items.append(api_str)
                combined_api_str = "; ".join(api_items)
                final_str = f'Role: {seq["role"]}; {combined_api_str}'
                revised_API_seqs['normal_seqs'].append(final_str)
            for seq in example_API_seqs['malicious_seqs']:
                api_items = []
                for seq_item in seq["seq"]:
                    api_str = f"API_{id_map[str(seq_item['id'])]}({seq_item['description']})"
                    api_items.append(api_str)
                combined_api_str = "; ".join(api_items)
                final_str = f'Role: {seq["role"]}; {combined_api_str}'
                revised_API_seqs['malicious_seqs'].append(final_str)
        # {
        #     'normal_seqs': [
        #         {'role':'','seq':[{"id":1,"description":""}, {"id":1,"description":""}]},
        #         {'role':'','seq':[{"id":1,"description":""}, {"id":1,"description":""}]}
        #     ], 
        #     'malicious_seqs': [
        #         {'role':'','seq':[{"id":1,"description":""}, {"id":1,"description":""}]},
        #         {'role':'','seq':[{"id":1,"description":""}, {"id":1,"description":""}]}
        #     ], 
        # }

        # 异步调用请求算法端进行流量数据扩增
        data_collect_url = f'http://{target_app.SFWAP_address}/data_collect'
        data = {
            'API_list': API_list_model_to_view(target_app.user_API_list), 
            'target_app': target_app_model_to_view(target_app),
        }
        if example_API_seqs and len(revised_API_seqs['normal_seqs']) > 0 and len(revised_API_seqs['malicious_seqs']) > 0:
            data['example_API_seqs'] = revised_API_seqs

        try:
            requests.post(data_collect_url, json=data)
        except requests.RequestException as e:
            return JsonResponse({
                'code': 500,
                'error': f'Error making data collection request to SFWAP-Detector: {str(e)}'
            },status=500)

        return JsonResponse({
            'code': 200,
            'message': 'User API list updated successfully, Data collection started'
        }, status=200)
    except json.JSONDecodeError:
        return JsonResponse({
            'code': 400,
            'error': 'Invalid JSON data'
        }, status=400)



# 前端页面中，更新API_list时，不能增加新的API，否则不能保证可以收集新API的参数集合。如果需要新增API，需先调用API发现并保证API发现结果包含新API
# PUT /api/user-api-list {'user_API_list':[{...},{...}]}
@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_api_list(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)
    if target_app.last_API_discovery_at is None:
        return JsonResponse({
            'code': 409,
            'error': 'The target application has never had API discovery'
        }, status=409)
    if target_app.detect_state == 'STARTED':
        return JsonResponse({
            'code': 409,
            'error': 'You cannot update the API list during detection'
        }, status=409)

    try:
        data = json.loads(request.body)
        user_api_list_data = data.get('user_API_list', [])
        valid_api_items: List[Dict] = []
        for api_data in user_api_list_data:
            result = validate_api(api_data)
            if isinstance(result, JsonResponse):
                return result
            valid_api_items.append(result)

        with transaction.atomic():
            for api in target_app.user_API_list.all():
                api.path_segment_list.all().delete()
                api.request_param_list.all().delete()
                api.request_data_fields.all().delete()
                api.delete()
            target_app.user_API_list.clear()

            for valid_api_item in valid_api_items:
                valid_api_item['api'].save()
                for segment in valid_api_item['path_segments']:
                    segment.save()
                for param in valid_api_item['request_params']:
                    param.save()
                for field in valid_api_item['request_data_fields']:
                    field.save()
                valid_api_item['api'].path_segment_list.set(valid_api_item['path_segments'])
                valid_api_item['api'].request_param_list.set(valid_api_item['request_params'])
                valid_api_item['api'].request_data_fields.set(valid_api_item['request_data_fields'])
                target_app.user_API_list.add(valid_api_item['api'])

        # 异步调用请求算法端进行流量数据扩增
        data_collect_url = f'http://{target_app.SFWAP_address}/data_collect'
        data = {'API_list': API_list_model_to_view(target_app.user_API_list), 'target_app': target_app_model_to_view(target_app)}
        try:
            requests.post(data_collect_url, json=data)
        except requests.RequestException as e:
            return JsonResponse({
                'code': 500,
                'error': f'Error making data collection request to SFWAP-Detector: {str(e)}'
            }, status=500)
        return JsonResponse({
            'code': 200,
            'message': 'User API list updated successfully, Data collection started'
        }, status=200)
    except json.JSONDecodeError:
        return JsonResponse({
            'code': 400,
            'error': 'Invalid JSON data'
        }, status=400)


# @api_view(['GET'])
# @permission_classes([IsAuthenticated])
# def data_collect(request):
#     app_id = request.query_params.get('app_id')
#     if not app_id:
#         return JsonResponse({'error': 'Missing target application ID'}, status=400)
#     try:
#         target_app = TargetApplication.objects.get(id=app_id, user=request.user)
#         data_collect_url = f'http://{target_app.SFWAP_address}/data_collect'
#         # {'normal_seqs': ["",], 'malicious_seqs':["",]}
#         data = {
#             'API_list': API_list_model_to_view(target_app.user_API_list), 
#             'target_app': target_app_model_to_view(target_app),
#             'example_API_seqs': json.loads(request.body).get('example_API_seqs')
#         }
#         try:
#             requests.post(data_collect_url, json=data)
#         except requests.RequestException as e:
#             return JsonResponse({'error': f'Error making data collection request to SFWAP-Detector: {str(e)}'},
#                                 status=500)
#     except TargetApplication.DoesNotExist:
#         return JsonResponse({'error': 'Target application not found or you do not have permission'}, status=404)
    


@api_view(['GET'])
@permission_classes([IsAuthenticated])
# 客户端轮询调用；API发现正在进行中
# {"api_discovery_status": 'IN_PROGRESS' if api_discovery_in_progress else 'AVAILABLE'}
def get_auto_API_discovery_status(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)
    try:
        response = requests.get(f'http://{target_app.SFWAP_address}/api_discovery/status')
        return JsonResponse({
            'code': response.status_code,
            'data': response.json()
        }, status=response.status_code)
    except requests.RequestException as e:
        return JsonResponse({
            'code': 500,
            'error': f'Error making auto API discovery state query request to SFWAP-Detector: {str(e)}'
        }, status=500)
    except ValueError:
        return JsonResponse({
            'code': 500,
            'error': 'Invalid JSON response from SFWAP-Detector'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def start_api_discovery(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)

    if target_app.is_draft:
        return JsonResponse({
            'code': 409,
            'error': 'API discovery is not available for staged target apps'
        }, status=409)
    if target_app.detect_state == 'STARTED':
        return JsonResponse({
            'code': 409,
            'error': 'You cannot do the API discovery during detection'
        }, status=409)

    sfwap_address = target_app.SFWAP_address
    mode = request.query_params.get('mode')
    if mode == 'AUTO':
        try:
            response = requests.post(f'http://{sfwap_address}/api_discovery', json=target_app_model_to_view(target_app))
            return JsonResponse({
                'code': response.status_code,
                'data': response.json()
            }, status=response.status_code)
        except requests.RequestException as e:
            return JsonResponse({
                'code': 500,
                'error': f'Error making auto API discovery start request to SFWAP-Detector: {str(e)}'
            }, status=500)
        except ValueError:
            return JsonResponse({
                'code': 500,
                'error': 'Invalid JSON response from SFWAP-Detector'
            }, status=500)
    elif mode == 'MANUAL':
        if target_app.last_API_discovery_at is None:
            return JsonResponse({
                'code': 409,
                'error': 'You cannot do the manual API discovery until any auto API discovery is finished'
            }, status=409)
        try:
            response = requests.post(f'http://{sfwap_address}/api_discovery/start',
                                     json=target_app_model_to_view(target_app))
            return JsonResponse({
                'code': response.status_code,
                'data': response.json()
            }, status=response.status_code)
        except requests.RequestException as e:
            return JsonResponse({
                'code': 500,
                'error': f'Error making manual API discovery start request to SFWAP-Detector: {str(e)}'
            }, status=500)
        except ValueError:
            return JsonResponse({
                'code': 500,
                'error': 'Invalid JSON response from SFWAP-Detector'
            }, status=500)
    else:
        return JsonResponse({
            'code': 400,
            'error': 'Invalid mode parameter'
        }, status=400)


def save_api_list(target_app, api_list_field_name, api_list_data):
    valid_api_items: List[Dict] = []
    for api_data in api_list_data:
        if api_data.get('request_method') not in ('POST', 'GET', 'PUT', 'DELETE'):
            continue
        # print(api_data)
        result = validate_api(api_data)
        if isinstance(result, JsonResponse):
            # print(result)
            return result.content
        valid_api_items.append(result)

    with transaction.atomic():
        api_list = getattr(target_app, api_list_field_name)
        for api in api_list.all():
            api.path_segment_list.all().delete()
            api.request_param_list.all().delete()
            api.request_data_fields.all().delete()
            api.delete()
        api_list.clear()

        print(f"Saving!!!{len(valid_api_items)}")

        for valid_api_item in valid_api_items:
            valid_api_item['api'].save()
            for segment in valid_api_item['path_segments']:
                segment.save()
            for param in valid_api_item['request_params']:
                param.save()
            for field in valid_api_item['request_data_fields']:
                field.save()
            valid_api_item['api'].path_segment_list.set(valid_api_item['path_segments'])
            valid_api_item['api'].request_param_list.set(valid_api_item['request_params'])
            valid_api_item['api'].request_data_fields.set(valid_api_item['request_data_fields'])
            api_list.add(valid_api_item['api'])

    return None


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def finish_api_discovery(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)

    if target_app.last_API_discovery_at is None:
        return JsonResponse({
            'code': 409,
            'error': 'You cannot do the manual API discovery until any auto API discovery is finished'
        }, status=409)
    if target_app.is_draft:
        return JsonResponse({
            'code': 409,
            'error': 'API discovery is not available for staged target apps'
        }, status=409)
    if target_app.detect_state == 'STARTED':
        return JsonResponse({
            'code': 409,
            'error': 'You cannot do the API discovery during detection'
        }, status=409)

    sfwap_address = target_app.SFWAP_address
    try:
        response = requests.get(f'http://{sfwap_address}/api_discovery/finish')

        discovered_api_list_data = response.json().get('discovered_API_list', [])

        print(f"Saving API list: {len(discovered_api_list_data)}")
        res = save_api_list(target_app, api_list_field_name='discovered_API_list', api_list_data=[
            api for api in discovered_api_list_data if api.get('request_method') in ('POST', 'GET', 'PUT', 'DELETE')
        ])
        if res:
            print(res.content)
        if target_app.detect_state == 'API_LIST_TO_DISCOVER':
            target_app.detect_state = 'API_LIST_TO_IMPROVE'
            target_app.save(update_fields=['detect_state'])
        target_app.last_API_discovery_at = timezone.now()
        target_app.save(update_fields=['last_API_discovery_at'])

        return JsonResponse({
            'code': response.status_code,
            'data': response.json()
        }, status=response.status_code)
    except requests.RequestException as e:
        return JsonResponse({
            'code': 500,
            'error': f'Error making manual API discovery stop request to SFWAP-Detector: {str(e)}'
        }, status=500)
    except Exception as e:
        return JsonResponse({
            'code': 500,
            'error': f'An error occurred during handling manual API discoveries: {str(e)}'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cancel_api_discovery(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)

    if target_app.last_API_discovery_at is None:
        return JsonResponse({
            'code': 409,
            'error': 'You cannot do the manual API discovery until any auto API discovery is finished'
        }, status=409)
    if target_app.is_draft:
        return JsonResponse({
            'code': 409,
            'error': 'API discovery is not available for staged target apps'
        }, status=409)
    if target_app.detect_state == 'STARTED':
        return JsonResponse({
            'code': 409,
            'error': 'You cannot do the API discovery during detection'
        }, status=409)

    sfwap_address = target_app.SFWAP_address
    try:
        response = requests.get(f'http://{sfwap_address}/api_discovery/cancel')
        return JsonResponse({
            'code': response.status_code,
            'data': response.json()
        }, status=response.status_code)
    except requests.RequestException as e:
        return JsonResponse({
            'code': 500,
            'error': f'Error making manual API discovery cancel request to SFWAP-Detector: {str(e)}'
        }, status=500)
    except ValueError:
        return JsonResponse({
            'code': 500,
            'error': 'Invalid JSON response from SFWAP-Detector'
        }, status=500)


# 接收算法端的API发现通知，由算法端调用
@api_view(['POST'])
def api_discovery_notification(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)
    # try:
    discovery_data = request.data
    # print(discovery_data)
    handle_api_discovery_notification(app_id, discovery_data)
    return JsonResponse({
        'code': 200,
        'message': 'Notification received and processing started'
    }, status=200)
    # except Exception as e:
    #     return JsonResponse({'error': str(e)}, status=500)


def get_feature_list(feature_list_field):
    feature_list = []
    for feature in feature_list_field.all():
        if feature.feature_type == 'SeqOccurTimeFeature':
            feature_data = {
                'id': feature.id,
                'name': feature.name,
                'description': feature.description,
                'string_list': feature.string_list,
                'type': 'SeqOccurTimeFeature'
            }
        else:
            feature_data = {
                'id': feature.id,
                'name': feature.name,
                'description': feature.description,
                'type': 'DetectFeature'
            }
        feature_list.append(feature_data)
    return feature_list


# GET /api/detect_feature/?app_id=<NUM>
# PUT /api/detect_feature/?app_id=<NUM> {'detect_feature_list':[{'id':<NUM>, 'name':'string', 'description:'string', 'type': 'SeqOccurTimeFeature', 'string_list':['', '']}]}
@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def detect_feature(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)

    if request.method == 'GET':
        feature_list = get_feature_list(target_app.detect_feature_list)
        return JsonResponse({
            'code': 200,
            'data': {
                'detect_feature_list': feature_list,
                'total': len(feature_list)
            }
        }, status=200)

    elif request.method == 'PUT':
        if target_app.detect_state == 'STARTED':
            return JsonResponse({
                'code': 409,
                'error': 'You cannot update the detect feature list during detection'
            }, status=409)
        try:
            data = json.loads(request.body)
            feature_list = data.get('detect_feature_list', [])
            updated_features = []

            for feature_data in feature_list:
                feature_id = feature_data.get('id')
                name = feature_data.get('name')
                description = feature_data.get('description')
                feature_type = feature_data.get('type')
                if not name or not description:
                    return JsonResponse({
                        'code': 400,
                        'error': f'Name and description are required for feature with data: {feature_data}'
                    }, status=400)

                if feature_type == 'SeqOccurTimeFeature':
                    string_list = feature_data.get('string_list')
                    if not string_list:
                        return JsonResponse({
                            'code': 400,
                            'error': f'string_list is required for SeqOccurTimeFeature with data: {feature_data}'
                        }, status=400)
                    if feature_id:
                        try:
                            feature = DetectFeature.objects.get(id=feature_id)
                        except DetectFeature.DoesNotExist:
                            feature = DetectFeature()
                    else:
                        feature = DetectFeature()
                    feature.feature_type = feature_type
                    feature.string_list = string_list
                elif feature_type == 'DetectFeature':
                    if feature_id:
                        try:
                            feature = DetectFeature.objects.get(id=feature_id)
                        except DetectFeature.DoesNotExist:
                            feature = DetectFeature()
                    else:
                        feature = DetectFeature()
                else:
                    return JsonResponse({
                        'code': 400,
                        'error': f'Invalid feature type in data: {feature_data}'
                    }, status=400)

                feature.name = name
                feature.description = description
                try:
                    feature.full_clean()
                    updated_features.append(feature)
                except ValidationError as e:
                    return JsonResponse({
                        'code': 400,
                        'error': str(e)
                    }, status=400)

            target_app.detect_feature_list.clear()
            for feature in updated_features:
                feature.save()
                # print(feature.feature_type)
                target_app.detect_feature_list.add(feature)
            return JsonResponse({
                'code': 200,
                'message': 'Detect features updated successfully'
            }, status=200)
        except json.JSONDecodeError:
            return JsonResponse({
                'code': 400,
                'error': 'Invalid JSON data'
            }, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_data_collection_status(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)
    try:
        response = requests.get(f'http://{target_app.SFWAP_address}/data_collect_status')
        return JsonResponse({
            'code':response.status_code, 
            'data':response.json()
        }, status=response.status_code)
    except requests.RequestException as e:
        return JsonResponse({
            'code': 500,
            'error': f'Error making auto data collection state query request to SFWAP-Detector: {str(e)}'
        }, status=500)
    except ValueError:
        return JsonResponse({
            'code': 500,
            'error': 'Invalid JSON response from SFWAP-Detector'
        }, status=500)
    
def compile_report(report):
    if not report:
        return None
    # 按行分割报告内容
    lines = report.strip().split('\n')
    # 去除空行
    valid_lines = [line for line in lines if line.strip()]
    # 跳过表头
    valid_lines = valid_lines[1:]

    result = []
    for line in valid_lines:
        # 分割每行数据
        parts = line.split()
        # 去除行名（如果是数字开头的行）
        if parts[0].isdigit():
            parts = parts[1:]
        # 尝试将每个部分转换为浮点数并添加到结果列表
        for part in parts:
            try:
                num = float(part)
                result.append(num)
            except ValueError:
                continue

    return result


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def construct_model(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)

    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)

    if target_app.is_draft:
        return JsonResponse({
            'code': 409,
            'error': 'Model construction is not available for staged target apps'
        }, status=409)
    if target_app.last_API_discovery_at is None:
        return JsonResponse({
            'code': 409,
            'error': 'Model construction is not available until the API discovery is finished'
        }, status=409)
    if target_app.detect_state == 'STARTED':
        return JsonResponse({
            'code': 409,
            'error': 'Model construction is not available during detection'
        }, status=409)

    user_API_list = API_list_model_to_view(target_app.user_API_list)
    detection_feature_list = get_feature_list(target_app.detect_feature_list)

    # 请求算法端构建模型，返回模型报告
    # 算法端：数据扩增&模型构建
    url = f'http://{target_app.SFWAP_address}/construct_model'
    data = {
        'target_app': target_app_model_to_view(target_app),
        'API_list': user_API_list,
        'detection_feature_list': detection_feature_list
    }

    try:
        response = requests.post(url, json=data)
        result = response.json()
        # print(result)
        error = result.get('error')
        if error:
            return JsonResponse({
                'code': 500,
                'error': 'Model construction error: ' + error
            }, status=500)
        message = result.get('message')
        if message:
            return JsonResponse({
                'code': 409,
                'error': message
            }, status=409)

        report = result.get('report')
        error_API_list = result.get('error_API_list')
        target_app.model_report = report
        target_app.last_model_construction_at = timezone.now()
        target_app.save(update_fields=['model_report', 'last_model_construction_at'])
        if target_app.detect_state == 'API_LIST_TO_IMPROVE':
            target_app.detect_state = 'MODEL_FEATURES_TO_CONFIGURE'
            target_app.save(update_fields=['detect_state'])
        return JsonResponse({
            'code': 200,
            'message': 'Model construction successful', 
            'data': {
                'report': compile_report(report), 
                'error_API_list': error_API_list
            }
        }, status=200)
    except requests.RequestException as e:
        return JsonResponse({
            'code': 500,
            'error': f'Error making model construction request: {str(e)}'
        }, status=500)
    except ValueError:
        return JsonResponse({
            'code': 500,
            'error': 'Invalid JSON response from model construction'
        }, status=500)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def detection_config(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)

    if request.method == 'GET':
        return JsonResponse({
            'code': 200,
            'data': {
                'enhanced_detection_enabled': target_app.enhanced_detection_enabled,
                'combined_data_duration': target_app.combined_data_duration
            }
        }, status=200)
    elif request.method == 'PUT':
        if target_app.detect_state == 'STARTED':
            return JsonResponse({
                'code': 409,
                'error': 'You cannot edit the detection config during the detection'
            }, status=409)
        if target_app.last_model_construction_at is None:
            return JsonResponse({
                'code': 409,
                'error': 'You cannot edit the detection config until the model construction finished'
            }, status=409)
        if target_app.last_API_discovery_at is None:
            return JsonResponse({
                'code': 409,
                'error': 'You cannot edit the detection config until the API discovery finished'
            }, status=409)
        if target_app.is_draft:
            return JsonResponse({
                'code': 409,
                'error': 'Detection configuration is not available for staged targets'
            }, status=409)

        data = json.loads(request.body)
        enhanced_detection_enabled = data.get('enhanced_detection_enabled')
        combined_data_duration = data.get('combined_data_duration')
        if not all([enhanced_detection_enabled, combined_data_duration]):
            return JsonResponse({
                'code': 400,
                'error': 'Missing required detection configuration fields'
            }, status=400)
        target_app.enhanced_detection_enabled = enhanced_detection_enabled
        target_app.combined_data_duration = combined_data_duration
        target_app.save(update_fields=['enhanced_detection_enabled', 'combined_data_duration'])
        try:
            target_app.full_clean()
            return JsonResponse({
                'code': 200,
                'message': 'Detection configuration successful'
            }, status=200)
        except ValidationError as e:
            return JsonResponse({
                'code': 400,
                'error': str(e)
            }, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def start_detection(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)

    # if target_app.detect_state == 'STARTED':
    #     return JsonResponse({'error': 'The detection is already started'}, status=409)
    if target_app.enhanced_detection_enabled is None or target_app.combined_data_duration is None:
        return JsonResponse({
            'code': 409,
            'error': 'You cannot start the detection until the detection configration is finished'
        }, status=409)
    if target_app.last_model_construction_at is None:
        return JsonResponse({
            'code': 409,
            'error': 'You cannot start the detection until the model construction is finished'
        }, status=409)
    if target_app.last_API_discovery_at is None:
        return JsonResponse({
            'code': 409,
            'error': 'You cannot start the detection until the API discovery is finished'
        }, status=409)
    if target_app.is_draft:
        return JsonResponse({
            'code': 409,
            'error': 'Detection is not available for staged targets'
        }, status=409)

    detection_start_url = f'http://{target_app.SFWAP_address}/detection/start'
    data = {'enhanced_detection_enabled': target_app.enhanced_detection_enabled,
            'combined_data_duration': target_app.combined_data_duration}
    try:
        response = requests.post(detection_start_url, json=data)
        result = response.json()
        error = result.get('error')
        if response.status_code != 200:
            return JsonResponse({
                'code': 409,
                'error': 'Detection start failed: ' + error
            }, status=409)
        else:
            target_app.detect_state = 'STARTED'
            target_app.save(update_fields=['detect_state'])
            return JsonResponse({
                'code': 200,
                'message': 'Detection started successfully'
            }, status=200)
    except requests.RequestException as e:
        return JsonResponse({
            'code': 500,
            'error': f'Detection start failed: {str(e)}'
        }, status=500)
    except ValueError:
        return JsonResponse({
            'code': 500,
            'error': 'Invalid JSON response from SFWAP-Detector'
        }, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def pause_detection(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)

    # if not target_app.detect_state == 'STARTED':
    #     return JsonResponse({'error': 'Target application is not started'}, status=409)

    detection_pause_url = f'http://{target_app.SFWAP_address}/detection/pause'
    try:
        response = requests.get(detection_pause_url)
        result = response.json()
        error = result.get('error')
        if response.status_code != 200:
            return JsonResponse({
                'code': 409,
                'error': 'Detection pause failed: ' + error
            }, status=409)
        else:
            target_app.detect_state = 'PAUSED'
            target_app.save(update_fields=['detect_state'])
            return JsonResponse({
                'code': 200,
                'message': 'Detection paused successfully'
            }, status=200)
    except requests.RequestException as e:
        return JsonResponse({
            'code': 500,
            'error': 'Detection pause failed: ' + str(e)
        }, status=500)
    except ValueError:
        return JsonResponse({
            'code': 500,
            'error': 'Invalid JSON response from SFWAP-Detector'
        }, status=500)


def update_detection_records(target_app):
    # 发起 HTTP 请求获取检测记录
    records_url = f'http://{target_app.SFWAP_address}/detection/records'
    try:
        response = requests.get(records_url)
        records_data = response.json().get('records')
        error = response.json().get('error')
        if error:
            return JsonResponse({
                'code': 500,
                'error': error
            }, status=500)
    except requests.RequestException as e:
        return JsonResponse({
            'code': 500,
            'error': f'Error fetching detection records: {str(e)}'
        }, status=500)
    except ValueError:
        return JsonResponse({
            'code': 500,
            'error': 'Invalid JSON response from SFWAP-Detector'
        }, status=500)

    # 检查并添加不重复的检测记录和流量数据
    # [{'detection_result':'','started_at':'','ended_at':''
    #   'traffic_data_list':[{...,'API':{'id':}}]}]
    for record_data in records_data:
        detection_result = record_data.get('detection_result')
        started_at = record_data.get('started_at')
        ended_at = record_data.get('ended_at')

        # 检查数据库中是否已存在相同的检测记录
        existing_record = DetectionRecord.objects.filter(
            app=target_app,
            detection_result=detection_result,
            started_at=started_at,
            ended_at=ended_at
        ).first()

        if existing_record:
            continue

        # 创建新的检测记录
        detection_record = DetectionRecord.objects.create(
            app=target_app,
            detection_result=detection_result,
            started_at=started_at,
            ended_at=ended_at
        )

        # 处理流量数据
        traffic_data_list = record_data.get('traffic_data_list', [])
        for traffic_data_info in traffic_data_list:
            accessed_at = traffic_data_info.get('accessed_at')
            method = traffic_data_info.get('method')
            url = traffic_data_info.get('url')
            header = traffic_data_info.get('header')
            data = traffic_data_info.get('data')
            status_code = traffic_data_info.get('status_code')
            api_info = traffic_data_info.get('API')
            data_detection_result = traffic_data_info.get('detection_result')

            api = None
            if api_info:
                api_id = api_info.get('id')
                if api_id:
                    try:
                        api = API.objects.get(id=int(api_id))
                    except API.DoesNotExist:
                        pass

            # # 检查数据库中是否已存在相同的流量数据
            # existing_traffic_data = TrafficData.objects.filter(
            #     method=method,
            #     header=header,
            #     url=url,
            #     data=data,
            #     status_code=status_code,
            #     accessed_at=accessed_at
            # ).first()

            # if existing_traffic_data:
            #     traffic_data = existing_traffic_data
            # else:
            traffic_data = TrafficData.objects.create(
                method=method,
                header=header,
                url=url,
                data=data,
                status_code=status_code,
                accessed_at=accessed_at,
                API=api,
                detection_result=data_detection_result,
            )

            detection_record.traffic_data_list.add(traffic_data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_detection_records(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)

    update_detection_records(target_app)

    # 查询并返回数据库中的检测记录
    detection_records = DetectionRecord.objects.filter(app=target_app).order_by('-ended_at')
    records_data = []

    for record in detection_records:
        traffic_data_list = []
        for traffic_data in record.traffic_data_list.all():
            traffic_data_info = {
                'accessed_at': traffic_data.accessed_at,
                'method': traffic_data.method,
                'url': traffic_data.url,
                'header': traffic_data.header,
                'data': traffic_data.data,
                'status_code': traffic_data.status_code,
                'detection_result': traffic_data.detection_result,
            }
            traffic_data_list.append(traffic_data_info)

        record_info = {
            'id': record.id,
            'detection_result': record.detection_result,
            'started_at': record.started_at,
            'ended_at': record.ended_at,
            'traffic_data_list': traffic_data_list
        }
        records_data.append(record_info)
    
    return JsonResponse({
        'code': 200,
        'data': {
            'detection_records': records_data,
            'total': len(records_data)
        }
    }, safe=False, status=200)



TIME_WINDOWS = {
    'TenMinutes': timezone.timedelta(minutes=10),
    'AnHour': timezone.timedelta(hours=1),
    'SixHours': timezone.timedelta(hours=6),
    'OneDay': timezone.timedelta(days=1),
    'ThreeDays': timezone.timedelta(days=3),
    'OneWeek': timezone.timedelta(weeks=1),
    'OneMonth': timezone.timedelta(days=30)
}

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_detection_records_v1(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)

    update_detection_records(target_app)

    global TIME_WINDOWS
    time_window = request.query_params.get('time_window')
    if time_window and (time_window not in TIME_WINDOWS):
        return JsonResponse({
            'code': 400,
            'error': 'Invalid request parameter time_window'
        }, status=400)
    detection_result = request.query_params.get('detection_result')
    if detection_result and (detection_result not in ['ALLOW', 'ALARM', 'INTERCEPTION']):
        return JsonResponse({
            'code': 400,
            'error': 'Invalid request parameter detection_result'
        }, status=400)

    detection_records = DetectionRecord.objects.filter(app=target_app).order_by('-ended_at')
    if detection_result:
        detection_records = detection_records.filter(detection_result=detection_result)
    if time_window:
        current_time = timezone.now()
        start_time = current_time - TIME_WINDOWS[time_window]
        detection_records = detection_records.filter(started_at__gte=start_time, ended_at__lte=current_time)

    try:
        paginator = CustomPagination()
        page = paginator.paginate_queryset(detection_records, request)


        return JsonResponse({
            'code': 200,
            'data': {
                'detection_records': [{
                    'id': record.id,
                    'detection_result': record.detection_result,
                    'started_at': record.started_at,
                    'ended_at': record.ended_at,
                    'traffic_data_size': len(record.traffic_data_list.all())
                } for record in (page if page else detection_records)],
                'total': paginator.page.paginator.count if page else len(detection_records),
                'next': paginator.get_next_link() if page else None,
                'previous': paginator.get_previous_link() if page else None
            }
        }, safe=False, status=200)
    except EmptyPage as e:
        return JsonResponse({
            'code': 404,
            'error': str(e)
        }, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_traffic_data_list(request):
    app_id = request.query_params.get('app_id')
    detection_record_id = request.query_params.get('detection_record_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)
    if not detection_record_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing detection record ID'
        }, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)

    try:
        record = DetectionRecord.objects.get(id=detection_record_id)
    except DetectionRecord.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Detection record not found'
        }, status=404)
    
    try:
        paginator = CustomPagination()
        page = paginator.paginate_queryset(record.traffic_data_list.all(), request)

        return JsonResponse({
            'code': 200,
            'data': {
                'traffic_data_list': [{
                    'accessed_at': traffic_data.accessed_at,
                    'method': traffic_data.method,
                    'url': traffic_data.url,
                    'header': traffic_data.header,
                    'data': traffic_data.data,
                    'status_code': traffic_data.status_code,
                    'detection_result': traffic_data.detection_result,
                } for traffic_data in (page if page else record.traffic_data_list.all())],
                'total': paginator.page.paginator.count if page else len(record.traffic_data_list.all()),
                'next': paginator.get_next_link() if page else None,
                'previous': paginator.get_previous_link() if page else None
            }
        }, safe=False, status=200)
    except EmptyPage as e:
        return JsonResponse({
            'code': 404,
            'error': str(e)
        }, status=404)



@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_detection_report(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)

    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)

    # 发起 HTTP 请求获取检测记录
    records_url = f'http://{target_app.SFWAP_address}/detection/records'
    try:
        response = requests.get(records_url)
        records_data = response.json().get('records')
        error = response.json().get('error')
        if error:
            return JsonResponse({
                'code': 500,
                'error': error
            }, status=500)
    except requests.RequestException as e:
        return JsonResponse({
            'code': 500,
            'error': f'Error fetching detection records: {str(e)}'
        }, status=500)
    except ValueError:
        return JsonResponse({
            'code': 500,
            'error': 'Invalid JSON response from SFWAP-Detector'
        }, status=500)

    # 检查并添加不重复的检测记录和流量数据
    # [{'detection_result':'','started_at':'','ended_at':''
    #   'traffic_data_list':[{...,'API':{'id':}}]}]
    for record_data in records_data:
        detection_result = record_data.get('detection_result')
        started_at = record_data.get('started_at')
        ended_at = record_data.get('ended_at')

        # 检查数据库中是否已存在相同的检测记录
        existing_record = DetectionRecord.objects.filter(
            app=target_app,
            detection_result=detection_result,
            started_at=started_at,
            ended_at=ended_at
        ).first()

        if existing_record:
            continue

        # 创建新的检测记录
        detection_record = DetectionRecord.objects.create(
            app=target_app,
            detection_result=detection_result,
            started_at=started_at,
            ended_at=ended_at
        )

        # 处理流量数据
        traffic_data_list = record_data.get('traffic_data_list', [])
        for traffic_data_info in traffic_data_list:
            accessed_at = traffic_data_info.get('accessed_at')
            method = traffic_data_info.get('method')
            url = traffic_data_info.get('url')
            header = traffic_data_info.get('header')
            data = traffic_data_info.get('data')
            status_code = traffic_data_info.get('status_code')
            api_info = traffic_data_info.get('API')
            data_detection_result = traffic_data_info.get('detection_result')

            api = None
            if api_info:
                api_id = api_info.get('id')
                if api_id:
                    try:
                        api = API.objects.get(id=int(api_id))
                    except API.DoesNotExist:
                        pass

            # 检查数据库中是否已存在相同的流量数据
            existing_traffic_data = TrafficData.objects.filter(
                method=method,
                header=header,
                url=url,
                data=data,
                status_code=status_code,
                accessed_at=accessed_at
            ).first()

            if existing_traffic_data:
                traffic_data = existing_traffic_data
            else:
                traffic_data = TrafficData.objects.create(
                    method=method,
                    header=header,
                    url=url,
                    data=data,
                    status_code=status_code,
                    accessed_at=accessed_at,
                    API=api,
                    detection_result=data_detection_result,
                )

            detection_record.traffic_data_list.add(traffic_data)

    from django.db.models import Count
    history_records = DetectionRecord.objects.filter(app=target_app)
    total_record_count = history_records.count()
    result_counts = history_records.values('detection_result').annotate(count=Count('id'))
    history_record_result_percentages = {}
    history_record_result_ids = {}
    for result in result_counts:
        history_record_result_percentages[result['detection_result']] = (result['count'] / total_record_count) * 100
        history_record_result_ids[result['detection_result']] = list(history_records.filter(detection_result=result['detection_result'])
                                                                     .order_by('-ended_at').values_list('id', flat=True))
    current_time = timezone.now()
    time_windows = [
        ('TenMinutes', timezone.timedelta(minutes=10)),
        ('AnHour', timezone.timedelta(hours=1)),
        ('SixHours', timezone.timedelta(hours=6)),
        ('OneDay', timezone.timedelta(days=1)),
        ('ThreeDays', timezone.timedelta(days=3)),
        ('OneWeek', timezone.timedelta(weeks=1)),
        ('OneMonth', timezone.timedelta(days=30))
    ]
    time_window_record_result_percentages = {}
    time_window_record_result_ids = {}
    for window_name, window_duration in time_windows:
        time_window_record_result_percentages[window_name] = {}
        time_window_record_result_ids[window_name] = {}
        start_time = current_time - window_duration
        filtered_records = DetectionRecord.objects.filter(started_at__gte=start_time, ended_at__lte=current_time)
        window_total_count = filtered_records.count()
        time_window_record_result_percentages[window_name]['total'] = window_total_count
        if window_total_count == 0:
            continue
        result_counts = filtered_records.values('detection_result').annotate(count=Count('id'))
        percentages = {}
        counts = {}
        for result in result_counts:
            percentages[result['detection_result']] = (result['count'] / window_total_count) * 100
            counts[result['detection_result']] = result['count']
            time_window_record_result_ids[window_name][result['detection_result']] = list(filtered_records
                .filter(detection_result=result['detection_result']).order_by('-ended_at').values_list('id', flat=True))
        time_window_record_result_percentages[window_name]['percentages'] = percentages
        time_window_record_result_percentages[window_name]['counts'] = counts
    
    history_traffic_datas = TrafficData.objects.filter(detectionrecord__in=history_records)
    total_traffic_data_count = history_traffic_datas.count()
    result_counts = history_traffic_datas.values('detection_result').annotate(count=Count('id'))
    history_traffic_data_result_percentages = {}
    for result in result_counts:
        history_traffic_data_result_percentages[result['detection_result']] = (result['count'] / total_traffic_data_count) * 100
    time_window_traffic_data_result_percentages = {}
    for window_name, window_duration in time_windows:
        time_window_traffic_data_result_percentages[window_name] = {}
        start_time = current_time - window_duration
        filtered_records = TrafficData.objects.filter(accessed_at__gte=start_time)
        window_total_count = filtered_records.count()
        time_window_traffic_data_result_percentages[window_name]['total'] = window_total_count
        if window_total_count == 0:
            continue
        result_counts = filtered_records.values('detection_result').annotate(count=Count('id'))
        percentages = {}
        counts = {}
        for result in result_counts:
            percentages[result['detection_result']] = (result['count'] / window_total_count) * 100
            counts[result['detection_result']] = result['count']
        time_window_traffic_data_result_percentages[window_name]['percentages'] = percentages
        time_window_traffic_data_result_percentages[window_name]['counts'] = counts

    API_report = []
    user_API_list = target_app.user_API_list.all()
    for api in user_API_list:
        API_traffic_datas = TrafficData.objects.filter(API=api)
        API_traffic_data_count = API_traffic_datas.count()
        result_counts = API_traffic_datas.values('detection_result').annotate(count=Count('id'))
        API_traffic_data_result_percentages = {}
        for result in result_counts:
            API_traffic_data_result_percentages[result['detection_result']] = (result['count'] / API_traffic_data_count) * 100
        time_window_API_traffic_data_result_percentages = {}
        for window_name, window_duration in time_windows:
            time_window_API_traffic_data_result_percentages[window_name] = {}
            start_time = current_time - window_duration
            filtered_records = TrafficData.objects.filter(accessed_at__gte=start_time, API=api)
            window_total_count = filtered_records.count()
            time_window_API_traffic_data_result_percentages[window_name]['total'] = window_total_count
            if window_total_count == 0:
                continue
            result_counts = filtered_records.values('detection_result').annotate(count=Count('id'))
            percentages = {}
            counts = {}
            for result in result_counts:
                percentages[result['detection_result']] = (result['count'] / window_total_count) * 100
                counts[result['detection_result']] = result['count']
            time_window_API_traffic_data_result_percentages[window_name]['percentages'] = percentages
            time_window_API_traffic_data_result_percentages[window_name]['counts'] = counts
        API_report.append({
            'API_id': api.id,
            'method': api.request_method,
            'sample_url': api.sample_url,
            'time_window_API_traffic_data_result_percentages': time_window_API_traffic_data_result_percentages
        })

    return JsonResponse({
        'code': 200,
        'data': {
            'report': {
                'total_detection_record_count': total_record_count,
                'history_record_result_percentages': history_record_result_percentages,
                'history_record_result_ids': history_record_result_ids,
                'time_window_record_result_percentages': time_window_record_result_percentages,
                'time_window_record_result_ids': time_window_record_result_ids,
                'total_traffic_data_count': total_traffic_data_count,
                'history_traffic_data_result_percentages': history_traffic_data_result_percentages,
                'time_window_traffic_data_result_percentages': time_window_traffic_data_result_percentages,
                'API_report': API_report
            }
        }
    }, safe=False, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_detection_report_v1(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)

    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)

    update_detection_records(target_app)

    from django.db.models import Count
    current_time = timezone.now()
    time_windows = [
        ('History', timezone.timedelta(days=5000)),
        ('TenMinutes', timezone.timedelta(minutes=10)),
        ('AnHour', timezone.timedelta(hours=1)),
        ('SixHours', timezone.timedelta(hours=6)),
        ('OneDay', timezone.timedelta(days=1)),
        ('ThreeDays', timezone.timedelta(days=3)),
        ('OneWeek', timezone.timedelta(weeks=1)),
        ('OneMonth', timezone.timedelta(days=30))
    ]
    time_window_record_result_percentages = {}
    time_window_record_result_ids = {}
    history_records = DetectionRecord.objects.filter(app=target_app)
    result_counts = history_records.values('detection_result').annotate(count=Count('id'))


    for window_name, window_duration in time_windows:
        time_window_record_result_percentages[window_name] = {}
        time_window_record_result_ids[window_name] = {}
        start_time = current_time - window_duration
        filtered_records = DetectionRecord.objects.filter(started_at__gte=start_time, ended_at__lte=current_time)
        window_total_count = filtered_records.count()
        time_window_record_result_percentages[window_name]['total'] = window_total_count
        if window_total_count == 0:
            continue
        result_counts = filtered_records.values('detection_result').annotate(count=Count('id'))
        percentages = {}
        counts = {}
        for result in result_counts:
            percentages[result['detection_result']] = (result['count'] / window_total_count) * 100
            counts[result['detection_result']] = result['count']
            time_window_record_result_ids[window_name][result['detection_result']] = list(filtered_records
                .filter(detection_result=result['detection_result']).order_by('-ended_at').values_list('id', flat=True))
        time_window_record_result_percentages[window_name]['percentages'] = percentages
        time_window_record_result_percentages[window_name]['counts'] = counts
    
    # history_traffic_datas = TrafficData.objects.filter(detectionrecord__in=history_records).order_by('-accessed_at')
    # total_traffic_data_count = history_traffic_datas.count()
    # result_counts = history_traffic_datas.values('detection_result').annotate(count=Count('id'))
    # history_traffic_data_result_percentages = {}
    # for result in result_counts:
    #     history_traffic_data_result_percentages[result['detection_result']] = (result['count'] / total_traffic_data_count) * 100
    time_window_traffic_data_result_percentages = {}
    for window_name, window_duration in time_windows:
        time_window_traffic_data_result_percentages[window_name] = {}
        start_time = current_time - window_duration
        filtered_records = TrafficData.objects.filter(accessed_at__gte=start_time)
        window_total_count = filtered_records.count()
        time_window_traffic_data_result_percentages[window_name]['total'] = window_total_count
        if window_total_count == 0:
            continue
        result_counts = filtered_records.values('detection_result').annotate(count=Count('id'))
        percentages = {}
        counts = {}
        for result in result_counts:
            percentages[result['detection_result']] = (result['count'] / window_total_count) * 100
            counts[result['detection_result']] = result['count']
        time_window_traffic_data_result_percentages[window_name]['percentages'] = percentages
        time_window_traffic_data_result_percentages[window_name]['counts'] = counts

    API_report = []
    user_API_list = target_app.user_API_list.all()
    for api in user_API_list:
        API_traffic_datas = TrafficData.objects.filter(API=api)
        API_traffic_data_count = API_traffic_datas.count()
        result_counts = API_traffic_datas.values('detection_result').annotate(count=Count('id'))
        API_traffic_data_result_percentages = {}
        for result in result_counts:
            API_traffic_data_result_percentages[result['detection_result']] = (result['count'] / API_traffic_data_count) * 100
        time_window_API_traffic_data_result_percentages = {}
        detection_record_ids = {}
        for window_name, window_duration in time_windows:
            time_window_API_traffic_data_result_percentages[window_name] = {}
            detection_record_ids[window_name] = {}
            start_time = current_time - window_duration
            filtered_records = TrafficData.objects.filter(accessed_at__gte=start_time, API=api)
            window_total_count = filtered_records.count()
            time_window_API_traffic_data_result_percentages[window_name]['total'] = window_total_count
            if window_total_count == 0:
                continue
            result_counts = filtered_records.values('detection_result').annotate(count=Count('id'))
            percentages = {}
            counts = {}
            for result in result_counts:
                percentages[result['detection_result']] = (result['count'] / window_total_count) * 100
                counts[result['detection_result']] = result['count']
                detection_record_ids[window_name][result['detection_result']] = [(DetectionRecord.objects.filter(traffic_data_list=data))[0].id 
                                                                                 for data in filtered_records.filter(detection_result=result['detection_result'])
                                                                                 .order_by('-accessed_at')]
            time_window_API_traffic_data_result_percentages[window_name]['percentages'] = percentages
            time_window_API_traffic_data_result_percentages[window_name]['counts'] = counts
        API_report.append({
            'API_id': api.id,
            'method': api.request_method,
            'sample_url': api.sample_url,
            'traffic_data_percentages': time_window_API_traffic_data_result_percentages,
            'detection_record_ids': detection_record_ids
        })

    return JsonResponse({
        'code': 200,
        'data': {
            'report': {
                'record_percentages': time_window_record_result_percentages,
                'record_ids': time_window_record_result_ids,
                'traffic_data_percentages': time_window_traffic_data_result_percentages,
                'API_report': API_report
            }
        }
    }, safe=False, status=200)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def get_detection_records_by_ids(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)

    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)
    
    ids = json.loads(request.body).get("record_id_list")
    
    if not ids or not (isinstance(ids, list)):
        return JsonResponse({
            'code': 400,
            'error': 'Invalid record_id_list'
        }, status=400)
    detection_records = [DetectionRecord.objects.get(id=_id) for _id in ids]
    return JsonResponse({
        'code': 200,
        'data': {
            'detection_records': [{
                'id': record.id,
                'detection_result': record.detection_result,
                'started_at': record.started_at,
                'ended_at': record.ended_at,
                'traffic_data_size': len(record.traffic_data_list.all())
            } for record in detection_records]
        }
    }, safe=False, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_detection_records_by_api(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)

    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)

    user_api_list = target_app.user_API_list.all()
    traffic_data_list = []

    for api in user_api_list:
        api_traffic_data = TrafficData.objects.filter(API=api).order_by('accessed_at')
        for traffic_data in api_traffic_data:
            traffic_data_info = {
                'id': traffic_data.id,
                'method': traffic_data.method,
                'header': traffic_data.header,
                'url': traffic_data.url,
                'data': traffic_data.data,
                'status_code': traffic_data.status_code,
                'accessed_at': traffic_data.accessed_at,
                'API_id': api.id,
                'detection_result': traffic_data.detection_result
            }
            traffic_data_list.append(traffic_data_info)

    return JsonResponse({
        'code': 200,
        'data': {
            'detection_records': traffic_data_list,
            'total': len(traffic_data_list)
        }
    }, safe=False, status=200)


@api_view(['GET'])
def load_target_app(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({'error': 'Missing target application ID'}, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id)
        return JsonResponse({
            'target_app': target_app_model_to_view(target_app),
            'detection_feature_list': get_feature_list(target_app.detect_feature_list)
        }, status=200)
    except TargetApplication.DoesNotExist:
        return JsonResponse({'error': 'Target application not found'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_manual_API_discovery_status(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({
            'code': 400,
            'error': 'Missing target application ID'
        }, status=400)

    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({
            'code': 404,
            'error': 'Target application not found or you do not have permission'
        }, status=404)
    # 发起 HTTP 请求获取检测记录
    records_url = f'http://{target_app.SFWAP_address}/api_discovery/manual/status'
    try:
        response = requests.get(records_url)
        return JsonResponse({
            'code': 200,
            'data': response.json()
        }, status=200)
    except requests.RequestException as e:
        return JsonResponse({
            'code': 500,
            'error': f'Error getting manual API discovery status: {str(e)}'
        }, status=500)
    except ValueError:
        return JsonResponse({
            'code': 500,
            'error': 'Invalid JSON response from SFWAP-Detector'
        }, status=500)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def check_deployment(request):
    SFWAP_address = json.loads(request.body).get("address")
    if not SFWAP_address:
        return JsonResponse({
            'code': 400,
            'error': 'Missing SFWAP address'
        }, status=400)

    check_url = f'http://{SFWAP_address}/check_deployment'
    try:
        response = requests.get(check_url)
        response.raise_for_status()
        return JsonResponse({
            'code': 200,
            'message': "The deployment is OK",
            'data': {
                'status': 'SUCCESS'
            }
        }, status=200)
    except Exception as e:
        return JsonResponse({
            'code': 200,
            'error': 'The deployment has problems or the SFWAP_address is incorrect',
            'data': {
                'status': 'FAIL'
            }
        }, status=200)


# from celery import shared_task

from .models import TargetApplication
from django.utils import timezone
from typing import Dict, List



def handle_api_discovery_notification(app_id, discovery_data):
    try:
        print("=============================================================================")
        target_app = TargetApplication.objects.get(id=app_id)
        discovered_api_list = [] 
        for discovered_api in discovery_data.get('discovered_API_list', []):
            if discovered_api.get('request_method') in ('POST', 'GET', 'PUT', 'DELETE'):
                discovered_api_list.append(discovered_api)

        # 更新 discovered_API_list
        error_response = save_api_list(target_app, 'discovered_API_list', discovered_api_list)
        if error_response:
            return {'error': error_response.content}

        # 更新 user_API_list
        if len(list(target_app.user_API_list.all())) == 0:
            error_response = save_api_list(target_app, 'user_API_list', discovered_api_list)
            if error_response:
                return {'error': error_response.content}

        # 更新状态
        if target_app.detect_state == 'API_LIST_TO_DISCOVER':
            target_app.detect_state = 'API_LIST_TO_IMPROVE'
            target_app.save(update_fields=['detect_state'])
        target_app.last_API_discovery_at = timezone.now()
        target_app.save(update_fields=['last_API_discovery_at'])

        print(f"size: {len(list(target_app.discovered_API_list.all()))}")

        return {'message': 'API discovery and update successful'}
    except TargetApplication.DoesNotExist:
        logger.error(f"Target application with id {app_id} not found.")
        return {'error': f"Target application with id {app_id} not found."}
    except Exception as e:
        logger.error(f"An error occurred during API discovery notification handling: {str(e)}")
        return {'error': str(e)}
