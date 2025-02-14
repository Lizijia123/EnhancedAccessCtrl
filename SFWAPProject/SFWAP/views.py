from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.hashers import make_password
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
import copy


@csrf_exempt
def register(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')

        if not username or not password or not email:
            return JsonResponse({'error': 'Missing required fields'}, status=400)

        if User.objects.filter(username=username).exists():
            return JsonResponse({'error': 'Username already exists'}, status=400)

        if User.objects.filter(email=email).exists():
            return JsonResponse({'error': 'Email already exists'}, status=400)

        hashed_password = make_password(password)
        user = User(username=username, email=email, password=hashed_password)
        user.save()

        return JsonResponse({'message': 'User registered successfully'}, status=201)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return JsonResponse({'message': 'User logged in successfully'}, status=200)
        else:
            return JsonResponse({'error': 'Invalid username or password'}, status=401)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@csrf_exempt
def user_logout(request):
    if request.method == 'POST':
        logout(request)
        return JsonResponse({'message': 'User logged out successfully'}, status=200)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def target_app(request):
    if request.method == 'GET':
        app_id = request.query_params.get('id')
        if not app_id:
            return JsonResponse({'error': 'Missing target application ID'}, status=400)

        try:
            target_app = TargetApplication.objects.get(id=app_id, user=request.user)
            login_credentials = []
            for credential in target_app.login_credentials.all():
                login_credentials.append({
                    'user_role': credential.user_role,
                    'username': credential.username,
                    'password': credential.password
                })

            response_data = {
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
                'login_credentials': login_credentials
            }
            return JsonResponse(response_data, status=200)
        except TargetApplication.DoesNotExist:
            return JsonResponse({'error': 'Target application not found or you do not have permission'}, status=404)

    elif request.method == 'POST':
        try:
            data = json.loads(request.body)
            APP_name = data.get('APP_name')
            APP_url = data.get('APP_url')
            user_behavior_cycle = data.get('user_behavior_cycle')
            SFWAP_address = data.get('SFWAP_address')
            description = data.get('description')
            login_credentials_data = data.get('login_credentials', [])
            is_draft = data.get('is_draft', False)

            if not all([APP_name, APP_url, user_behavior_cycle, SFWAP_address, description,
                        len(login_credentials_data) >= 2]):
                return JsonResponse({'error': 'Missing required fields or insufficient login credentials'}, status=400)

            if TargetApplication.objects.filter(APP_name=APP_name).exists():
                return JsonResponse({'error': 'APP_name already exists'}, status=400)

            target_app = TargetApplication(
                APP_name=APP_name,
                APP_url=APP_url,
                user_behavior_cycle=user_behavior_cycle,
                SFWAP_address=SFWAP_address,
                description=description,
                user=request.user,
                is_draft=is_draft
            )
            target_app.full_clean()
            target_app.save()

            for credential_data in login_credentials_data:
                user_role = credential_data.get('user_role')
                username = credential_data.get('username')
                password = credential_data.get('password')

                if not all([user_role, username, password]):
                    target_app.delete()
                    return JsonResponse({'error': 'Missing fields in login credential'}, status=400)

                credential = LoginCredential(
                    user_role=user_role,
                    username=username,
                    password=password
                )
                credential.full_clean()
                credential.save()
                target_app.login_credentials.add(credential)

            response_data = {
                'message': 'Target application created successfully',
                'created_at': target_app.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': target_app.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_draft': target_app.is_draft,
                'last_API_discovery_at': None,
                'last_model_construction_at': None
            }
            return JsonResponse(response_data, status=201)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    elif request.method == 'PUT':
        try:
            app_id = request.query_params.get('id')
            if not app_id:
                return JsonResponse({'error': 'Missing target application ID'}, status=400)

            try:
                target_app = TargetApplication.objects.get(id=app_id, user=request.user)
            except TargetApplication.DoesNotExist:
                return JsonResponse({'error': 'Target application not found or you do not have permission'}, status=404)

            data = json.loads(request.body)
            is_draft = data.get('is_draft')

            if is_draft is not None:
                if is_draft:
                    return JsonResponse({'error': 'You cannot change the application to draft status when updating.'},
                                        status=400)
                target_app.is_draft = False

            APP_name = data.get('APP_name', target_app.APP_name)
            APP_url = data.get('APP_url', target_app.APP_url)
            user_behavior_cycle = data.get('user_behavior_cycle', target_app.user_behavior_cycle)
            SFWAP_address = data.get('SFWAP_address', target_app.SFWAP_address)
            description = data.get('description', target_app.description)
            login_credentials_data = data.get('login_credentials')

            if TargetApplication.objects.filter(APP_name=APP_name).exclude(id=app_id).exists():
                return JsonResponse({'error': 'APP_name already exists'}, status=400)

            if login_credentials_data and len(login_credentials_data) < 2:
                return JsonResponse({'error': 'Insufficient login credentials'}, status=400)

            target_app.APP_name = APP_name
            target_app.APP_url = APP_url
            target_app.user_behavior_cycle = user_behavior_cycle
            target_app.SFWAP_address = SFWAP_address
            target_app.description = description
            target_app.full_clean()
            target_app.save()

            if login_credentials_data:
                target_app.login_credentials.all().delete()
                for credential_data in login_credentials_data:
                    user_role = credential_data.get('user_role')
                    username = credential_data.get('username')
                    password = credential_data.get('password')

                    if not all([user_role, username, password]):
                        return JsonResponse({'error': 'Missing fields in login credential'}, status=400)

                    credential = LoginCredential(
                        user_role=user_role,
                        username=username,
                        password=password
                    )
                    credential.full_clean()
                    credential.save()
                    target_app.login_credentials.add(credential)

            response_data = {
                'message': 'Target application updated successfully',
                'created_at': target_app.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                'updated_at': target_app.updated_at.strftime('%Y-%m-%d %H:%M:%S'),
                'is_draft': target_app.is_draft,
                'last_API_discovery_at': target_app.last_API_discovery_at.strftime(
                    '%Y-%m-%d %H:%M:%S') if target_app.last_API_discovery_at else None,
                'last_model_construction_at': target_app.last_model_construction_at.strftime(
                    '%Y-%m-%d %H:%M:%S') if target_app.last_model_construction_at else None
            }
            return JsonResponse(response_data, status=200)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)
        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    elif request.method == 'DELETE':
        app_id = request.query_params.get('id')
        if not app_id:
            return JsonResponse({'error': 'Missing target application ID'}, status=400)

        try:
            target_app = TargetApplication.objects.get(id=app_id, user=request.user)
            target_app.delete()
            return JsonResponse({'message': 'Target application deleted successfully'}, status=200)
        except TargetApplication.DoesNotExist:
            return JsonResponse({'error': 'Target application not found or you do not have permission'}, status=404)

    return JsonResponse({'error': 'Invalid request method'}, status=405)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_api_lists(request):
    app_id = request.query_params.get('id')
    if not app_id:
        return JsonResponse({'error': 'Missing target application ID'}, status=400)

    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)

        discovered_API_list = []
        for api in target_app.discovered_API_list.all():
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
                'sample_url': api.sample_url,
                'sample_request_data': api.sample_request_data,
                'request_method': api.request_method,
                'function_description': api.function_description,
                'permission_info': api.permission_info,
                'path_segment_list': path_segment_list,
                'request_param_list': request_param_list,
                'request_data_fields': request_data_fields
            }
            discovered_API_list.append(api_info)

        user_API_list = []
        for api in target_app.user_API_list.all():
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
                'sample_url': api.sample_url,
                'sample_request_data': api.sample_request_data,
                'request_method': api.request_method,
                'function_description': api.function_description,
                'permission_info': api.permission_info,
                'path_segment_list': path_segment_list,
                'request_param_list': request_param_list,
                'request_data_fields': request_data_fields
            }
            user_API_list.append(api_info)

        response_data = {
            'discovered_API_list': discovered_API_list,
            'user_API_list': user_API_list
        }
        return JsonResponse(response_data, status=200)
    except TargetApplication.DoesNotExist:
        return JsonResponse({'error': 'Target application not found or you do not have permission'}, status=404)


def validate_and_save_api(api_data):
    function_description = api_data.get('function_description')
    permission_info = api_data.get('permission_info')
    if not function_description or not permission_info:
        return JsonResponse({
            'error': 'Each API must have non - empty function_description and permission_info'
        }, status=400)

    sample_url = api_data.get('sample_url')
    sample_request_data = api_data.get('sample_request_data')
    request_method = api_data.get('request_method')

    api = API(
        sample_url=sample_url,
        sample_request_data=sample_request_data,
        request_method=request_method,
        function_description=function_description,
        permission_info=permission_info
    )
    try:
        api.full_clean()
        api.save()
    except ValidationError as e:
        return JsonResponse({'error': f'Invalid API data: {str(e)}'}, status=400)

    path_segment_list_data = api_data.get('path_segment_list', [])
    for segment_data in path_segment_list_data:
        name = segment_data.get('name')
        is_path_variable = segment_data.get('is_path_variable')
        if not name or is_path_variable is None:
            return JsonResponse({
                'error': 'Each path segment must have a non - empty name and a valid is_path_variable value'
            }, status=400)
        segment = PathSegment(name=name, is_path_variable=is_path_variable)
        try:
            segment.full_clean()
            segment.save()
            api.path_segment_list.add(segment)
        except ValidationError as e:
            return JsonResponse({'error': f'Invalid path segment data: {str(e)}'}, status=400)

    request_param_list_data = api_data.get('request_param_list', [])
    for param_data in request_param_list_data:
        name = param_data.get('name')
        is_necessary = param_data.get('is_necessary')
        if not name or is_necessary is None:
            return JsonResponse({
                'error': 'Each request param must have a non - empty name and a valid is_necessary value'
            }, status=400)
        param = RequestParam(name=name, is_necessary=is_necessary)
        try:
            param.full_clean()
            param.save()
            api.request_param_list.add(param)
        except ValidationError as e:
            return JsonResponse({'error': f'Invalid request param data: {str(e)}'}, status=400)

    request_data_fields_data = api_data.get('request_data_fields', [])
    for field_data in request_data_fields_data:
        name = field_data.get('name')
        type_ = field_data.get('type')
        if not name or not type_ or type_ not in ['String', 'Number', 'List', 'Object']:
            return JsonResponse({
                'error': 'Each request data field must have a non - empty name and a valid type (String, Number, List, Object)'
            }, status=400)
        field = RequestDataField(name=name, type=type_)
        try:
            field.full_clean()
            field.save()
            api.request_data_fields.add(field)
        except ValidationError as e:
            return JsonResponse({'error': f'Invalid request data field data: {str(e)}'}, status=400)

    return api


@api_view(['PUT'])
@permission_classes([IsAuthenticated])
def update_user_api_list(request):
    print(json.loads(request.body))
    app_id = request.query_params.get('id')
    if not app_id:
        return JsonResponse({'error': 'Missing target application ID'}, status=400)

    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({'error': 'Target application not found or you do not have permission'}, status=404)

    try:
        data = json.loads(request.body)
        user_api_list_data = data.get('user_API_list', [])

        # 清空原有的 user_API_list
        target_app.user_API_list.clear()

        for api_data in user_api_list_data:
            result = validate_and_save_api(api_data)
            if isinstance(result, JsonResponse):
                return result
            target_app.user_API_list.add(result)

        return JsonResponse({'message': 'User API list updated successfully'}, status=200)

    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON data'}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def api_discovery(request):
    app_id = request.query_params.get('id')
    if not app_id:
        return JsonResponse({'error': 'Missing target application ID'}, status=400)

    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({'error': 'Target application not found or you do not have permission'}, status=404)

    sfwap_address = target_app.SFWAP_address
    discovery_url = f'http://{sfwap_address}/api_discovery'

    try:
        response = requests.get(discovery_url)
        response.raise_for_status()
        discovery_data = response.json()
        discovered_api_list_data = discovery_data.get('discovered_API_list', [])
    except requests.RequestException as e:
        return JsonResponse({'error': f'Error making API discovery request: {str(e)}'}, status=500)
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON response from API discovery'}, status=500)

    # 清空原有的 discovered_API_list
    target_app.discovered_API_list.clear()

    for api_data in discovered_api_list_data:
        result = validate_and_save_api(api_data)
        if isinstance(result, JsonResponse):
            return result
        target_app.discovered_API_list.add(result)

    # # 深拷贝 discovered_API_list 到 user_API_list
    # target_app.user_API_list.clear()
    # for api in target_app.discovered_API_list.all():
    #     new_api = copy.deepcopy(api)
    #     new_api.pk = None
    #     new_api.save()
    #     for segment in api.path_segment_list.all():
    #         new_segment = copy.deepcopy(segment)
    #         new_segment.pk = None
    #         new_segment.save()
    #         new_api.path_segment_list.add(new_segment)
    #     for param in api.request_param_list.all():
    #         new_param = copy.deepcopy(param)
    #         new_param.pk = None
    #         new_param.save()
    #         new_api.request_param_list.add(new_param)
    #     for field in api.request_data_fields.all():
    #         new_field = copy.deepcopy(field)
    #         new_field.pk = None
    #         new_field.save()
    #         new_api.request_data_fields.add(new_field)
    #     target_app.user_API_list.add(new_api)

    # 更新 last_API_discovery_at 为当前时间，不改变 updated_at
    target_app.last_API_discovery_at = timezone.now()
    target_app.save(update_fields=['last_API_discovery_at'])

    return JsonResponse({'message': 'API discovery and update successful'}, status=200)
