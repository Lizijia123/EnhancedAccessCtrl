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
from .tasks import handle_api_discovery_notification


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


def get_target_app_info(target_app):
    login_credentials = []
    for credential in target_app.login_credentials.all():
        login_credentials.append({
            'user_role': credential.user_role,
            'username': credential.username,
            'password': credential.password
        })

    return {
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
        'detect_state': target_app.detect_state
    }


@api_view(['GET', 'POST', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def target_app(request):
    if request.method == 'GET':
        app_id = request.query_params.get('id')
        if not app_id:
            return JsonResponse({'error': 'Missing target application ID'}, status=400)
        try:
            target_app = TargetApplication.objects.get(id=app_id, user=request.user)
            return JsonResponse(get_target_app_info(target_app), status=200)
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
            is_draft = data.get('is_draft')

            if not all([APP_name, APP_url, user_behavior_cycle, SFWAP_address, description,
                        len(login_credentials_data) >= 2]):
                return JsonResponse({'error': 'Missing required fields or insufficient login credentials'}, status=400)

            if TargetApplication.objects.filter(APP_name=APP_name).exists():
                return JsonResponse({'error': 'APP_name already exists'}, status=400)

            detect_state = 'BASIC_INFO_TO_CONFIGURE' if is_draft else 'API_LIST_TO_DISCOVER'

            # TODO:将特征集合设置为通用特征基线
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
            # is_draft = data.get('is_draft')
            #
            # if is_draft is not None:
            #     if is_draft:
            #         return JsonResponse({'error': 'You cannot change the application to draft status when updating.'},
            #                             status=400)
            #     target_app.is_draft = False

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


def get_API_list(api_list_field):
    API_list = []
    for api in api_list_field.all():
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
            'request_data_fields': request_data_fields
        }
        API_list.append(api_info)
    return API_list


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_api_lists(request):
    app_id = request.query_params.get('id')
    if not app_id:
        return JsonResponse({'error': 'Missing target application ID'}, status=400)

    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
        discovered_API_list = get_API_list(target_app.discovered_API_list)
        user_API_list = get_API_list(target_app.user_API_list)
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
        if not name or not type_ or type_ not in ['String', 'Number', 'Boolean', 'List', 'Object']:
            return JsonResponse({
                'error': 'Each request data field must have a non - empty name and a valid type (String, Number, Boolean, List, Object)'
            }, status=400)
        field = RequestDataField(name=name, type=type_)
        try:
            field.full_clean()
            field.save()
            api.request_data_fields.add(field)
        except ValidationError as e:
            return JsonResponse({'error': f'Invalid request data field data: {str(e)}'}, status=400)

    return api


# 前端页面中，更新API_list时，不能增加新的API，否则不能保证可以收集新API的参数集合。如果需要新增API，需先调用API发现并保证API发现结果包含新API
# PUT /api/user-api-list {'user_API_list':[{...},{...}]}
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

    if target_app.last_API_discovery_at is None:
        return JsonResponse({'error': 'The target application has never had API discovery'}, status=400)
    if target_app.detect_state == 'STARTED':
        return JsonResponse({'error': 'Please pause the detection first'}, status=400)

    try:
        data = json.loads(request.body)
        user_api_list_data = data.get('user_API_list', [])

        # 清空原有的 user_API_list 为了实现简单，删除并重新创建，而非更新
        # 获取并删除原有的 user_API_list 及其关联对象
        for api in target_app.user_API_list.all():
            api.path_segment_list.all().delete()
            api.request_param_list.all().delete()
            api.request_data_fields.all().delete()
            api.delete()
        target_app.user_API_list.clear()

        for api_data in user_api_list_data:
            result = validate_and_save_api(api_data)
            if isinstance(result, JsonResponse):
                return result
            target_app.user_API_list.add(result)

        # 异步调用请求算法端进行流量数据扩增
        data_collect_url = f'http://{target_app.SFWAP_address}/data_collect'
        data = {'API_list': get_API_list(target_app.user_API_list)}
        try:
            requests.post(data_collect_url, json=data)
        except requests.RequestException as e:
            return JsonResponse({'error': f'Error making data collection request: {str(e)}'}, status=500)

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

    if target_app.is_draft:
        return JsonResponse({'error': 'API discovery is not available for staged target apps'}, status=400)
    if target_app.detect_state == 'STARTED':
        return JsonResponse({'error': 'Please pause the detection first'}, status=400)

    sfwap_address = target_app.SFWAP_address
    mode = request.query_params.get('mode')
    discovery_url = f'http://{sfwap_address}/api_discovery'
    data = get_target_app_info(target_app)

    if mode == 'AUTO':
        try:
            response = requests.post(discovery_url, json=data)
            response.raise_for_status()
            discovery_data = response.json()
            discovered_api_list_data = discovery_data.get('discovered_API_list', [])
        except requests.RequestException as e:
            return JsonResponse({'error': f'Error making API discovery request: {str(e)}'}, status=500)
        except ValueError:
            return JsonResponse({'error': 'Invalid JSON response from API discovery'}, status=500)

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
                return result
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

        return JsonResponse({'message': 'API discovery and update successful'}, status=200)
    elif mode == 'MANUAL':
        try:
            requests.get(discovery_url)
            return JsonResponse({'message': 'OK'}, status=200)
        except requests.RequestException as e:
            return JsonResponse({'error': f'Error making API discovery request: {str(e)}'}, status=500)
    else:
        return JsonResponse({'error': 'Invalid mode parameter'}, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def stop_api_discovery(request):
    pass

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def cancel_api_discovery(request):
    # TODO
    pass

# 接收算法端的API发现通知
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def api_discovery_notification(request):
    app_id = request.query_params.get('id')
    if not app_id:
        return JsonResponse({'error': 'Missing target application ID'}, status=400)

    try:
        discovery_data = request.data
        handle_api_discovery_notification.delay(app_id, discovery_data)
        return JsonResponse({'message': 'Notification received and processing started'}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)


def get_feature_list(feature_list_field):
    feature_list = []
    for feature in feature_list_field.all():
        if isinstance(feature, SeqOccurTimeFeature):
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
# DELETE /api/detect_feature/?app_id=<NUM>&feature_id=<NUM>
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([IsAuthenticated])
def detect_feature(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({'error': 'Missing target application ID'}, status=400)

    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({'error': 'Target application not found or you do not have permission'}, status=404)

    if request.method == 'GET':
        feature_list = get_feature_list(target_app.detect_feature_list)
        return JsonResponse({'detect_feature_list': feature_list}, status=200)

    elif request.method == 'PUT':
        if target_app.detect_state == 'STARTED':
            return JsonResponse({'error': 'Please pause the detection first'}, status=400)

        try:
            data = json.loads(request.body)
            feature_list = data.get('detect_feature_list', [])
            updated_features = []

            # 先清空原有的特征列表
            target_app.detect_feature_list.clear()

            for feature_data in feature_list:
                feature_id = feature_data.get('id')
                name = feature_data.get('name')
                description = feature_data.get('description')
                feature_type = feature_data.get('type')

                if not name or not description:
                    return JsonResponse(
                        {'error': f'Name and description are required for feature with data: {feature_data}'},
                        status=400)

                if feature_type == 'SeqOccurTimeFeature':
                    string_list = feature_data.get('string_list')
                    if not string_list:
                        return JsonResponse(
                            {'error': f'string_list is required for SeqOccurTimeFeature with data: {feature_data}'},
                            status=400)
                    if feature_id:
                        try:
                            feature = SeqOccurTimeFeature.objects.get(id=feature_id)
                        except SeqOccurTimeFeature.DoesNotExist:
                            feature = SeqOccurTimeFeature()
                    else:
                        feature = SeqOccurTimeFeature()
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
                    return JsonResponse({'error': f'Invalid feature type in data: {feature_data}'}, status=400)

                feature.name = name
                feature.description = description

                try:
                    feature.full_clean()
                    feature.save()
                    updated_features.append(feature)
                except ValidationError as e:
                    # 如果有一个特征验证失败，删除之前保存的特征
                    for saved_feature in updated_features:
                        saved_feature.delete()
                    return JsonResponse({'error': str(e)}, status=400)

            for feature in updated_features:
                target_app.detect_feature_list.add(feature)

            return JsonResponse({'message': 'Detect features updated successfully'}, status=200)

        except json.JSONDecodeError:
            return JsonResponse({'error': 'Invalid JSON data'}, status=400)

    elif request.method == 'DELETE':
        if target_app.detect_state == 'STARTED':
            return JsonResponse({'error': 'Please pause the detection first'}, status=400)

        feature_id = request.query_params.get('feature_id')
        if not feature_id:
            return JsonResponse({'error': 'Feature ID is required'}, status=400)

        try:
            feature = target_app.detect_feature_list.get(id=feature_id)
            feature.delete()
            return JsonResponse({'message': 'Detect feature deleted successfully'}, status=200)
        except DetectFeature.DoesNotExist:
            return JsonResponse({'error': 'Detect feature not found in the target application'}, status=404)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def construct_model(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({'error': 'Missing target application ID'}, status=400)

    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({'error': 'Target application not found or you do not have permission'}, status=404)

    if target_app.is_draft:
        return JsonResponse({'error': 'Model construction is not available for staged target apps'}, status=409)
    if target_app.last_API_discovery_at is None:
        return JsonResponse({'error': 'Model construction is not available until the API discovery is finished'},
                            status=409)
    if target_app.detect_state == 'STARTED':
        return JsonResponse({'error': 'Please pause the detection first'}, status=400)

    user_API_list = get_API_list(target_app.user_API_list)
    detection_feature_list = get_feature_list(target_app.detect_feature_list)

    # 请求算法端构建模型，返回模型报告
    # 算法端：数据扩增&模型构建
    url = f'http://{target_app.SFWAP_address}/construct_model'
    data = {
        'target_app': get_target_app_info(target_app),
        'API_list': user_API_list,
        'detection_feature_list': detection_feature_list
    }

    try:
        response = requests.post(url, json=data)
        response.raise_for_status()
        result = response.json()

        error = result.get('error')
        if error:
            return JsonResponse({'error': 'Model construction error: ' + error}, status=500)

        report = result.get('report')
        error_API_list = result.get('error_API_list')

        # 更新目标应用的属性
        target_app.model_report = report
        target_app.last_model_construction_at = timezone.now()
        target_app.save(update_fields=['model_report', 'last_model_construction_at'])

        if target_app.detect_state == 'API_LIST_TO_IMPROVE':
            target_app.detect_state = 'MODEL_FEATURES_TO_IMPROVE'
            target_app.save(update_fields=['detect_state'])

        return JsonResponse(
            {'message': 'Model construction successful', 'report': report, 'error_API_list': error_API_list},
            status=200)

    except requests.RequestException as e:
        return JsonResponse({'error': f'Error making model construction request: {str(e)}'}, status=500)
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON response from model construction'}, status=500)


@api_view(['GET', 'PUT'])
@permission_classes([IsAuthenticated])
def detection_config(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({'error': 'Missing target application ID'}, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({'error': 'Target application not found or you do not have permission'}, status=404)

    if request.method == 'GET':
        return JsonResponse({
            'enhanced_detection_enabled': target_app.enhanced_detection_enabled,
            'combined_data_duration': target_app.combined_data_duration
        })
    elif request.method == 'PUT':
        if target_app.detect_state == 'STARTED':
            return JsonResponse({'error': 'Please pause the detection first'}, status=409)
        if target_app.last_model_construction_at is None:
            return JsonResponse({'error': 'Please finish the model construction first'}, status=409)
        if target_app.last_API_discovery_at is None:
            return JsonResponse({'error': 'Please finish the API discovery first'}, status=409)
        if target_app.is_draft:
            return JsonResponse({'error': 'Detection configuration is not available for staged targets'}, status=409)

        data = json.loads(request.body)
        enhanced_detection_enabled = data.get('enhanced_detection_enabled')
        combined_data_duration = data.get('combined_data_duration')
        if not all([enhanced_detection_enabled, combined_data_duration]):
            return JsonResponse({'error': 'Missing required fields or insufficient login credentials'}, status=400)
        target_app.enhanced_detection_enabled = enhanced_detection_enabled
        target_app.combined_data_duration = combined_data_duration
        target_app.save(update_fields=['enhanced_detection_enabled', 'combined_data_duration'])
        try:
            target_app.full_clean()
            return JsonResponse({'message': 'Detection configuration successful'}, status=200)
        except ValidationError as e:
            return JsonResponse({'error': str(e)}, status=400)


@api_view(['GET'])
def start_detection(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({'error': 'Missing target application ID'}, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({'error': 'Target application not found or you do not have permission'}, status=404)

    if target_app.detect_state == 'STARTED':
        return JsonResponse({'error': 'The detection is already started'}, status=409)
    if target_app.enhanced_detection_enabled is None or target_app.combined_data_duration is None:
        return JsonResponse({'error': 'Please finish the detection configration first'}, status=409)
    if target_app.last_model_construction_at is None:
        return JsonResponse({'error': 'Please finish the model construction first'}, status=409)
    if target_app.last_API_discovery_at is None:
        return JsonResponse({'error': 'Please finish the API discovery first'}, status=409)
    if target_app.is_draft:
        return JsonResponse({'error': 'Detection is not available for staged targets'}, status=409)

    detection_start_url = f'http://{target_app.SFWAP_address}/detection/start'
    data = {'enhanced_detection_enabled': target_app.enhanced_detection_enabled,
            'combined_data_duration': target_app.combined_data_duration}
    try:
        response = requests.post(detection_start_url, json=data)
        response.raise_for_status()
        result = response.json()
        info = result.get('info')
        if response.status_code != 200:
            return JsonResponse({'error': 'Detection start failed: ' + info}, status=500)
        else:
            target_app.detect_state = 'STARTED'
            return JsonResponse({'message': 'Detection start successful'}, status=200)
    except requests.RequestException as e:
        return JsonResponse({'error': f'Detection start failed: {str(e)}'}, status=500)
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON response from detection start request'}, status=500)


@api_view(['GET'])
def pause_detection(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({'error': 'Missing target application ID'}, status=400)
    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({'error': 'Target application not found or you do not have permission'}, status=404)

    if not target_app.detect_state == 'STARTED':
        return JsonResponse({'error': 'Target application is not started'}, status=409)

    detection_pause_url = f'http://{target_app.SFWAP_address}/detection/pause'
    try:
        response = requests.get(detection_pause_url)
        response.raise_for_status()
        result = response.json()
        info = result.get('info')
        if response.status_code != 200:
            return JsonResponse({'error': 'Detection pause failed: ' + info}, status=500)
        else:
            target_app.detect_state = 'PAUSED'
            return JsonResponse({'message': 'Detection pause successful'}, status=200)
    except requests.RequestException as e:
        return JsonResponse({'error': 'Detection pause failed: ' + str(e)}, status=500)
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON response from pause request'}, status=500)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_detection_records_by_combination(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({'error': 'Missing target application ID'}, status=400)

    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({'error': 'Target application not found or you do not have permission'}, status=404)

    # 发起 HTTP 请求获取检测记录
    records_url = f'http://{target_app.SFWAP_address}/detection/records'
    try:
        response = requests.get(records_url)
        response.raise_for_status()
        records_data = response.json()
    except requests.RequestException as e:
        return JsonResponse({'error': f'Error fetching detection records: {str(e)}'}, status=500)
    except ValueError:
        return JsonResponse({'error': 'Invalid JSON response from detection records API'}, status=500)

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
                        api = API.objects.get(id=api_id)
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

    # 查询并返回数据库中的检测记录
    detection_records = DetectionRecord.objects.filter(app=target_app).order_by('ended_at')
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
            'detection_result': record.detection_result,
            'started_at': record.started_at,
            'ended_at': record.ended_at,
            'traffic_data_list': traffic_data_list
        }
        records_data.append(record_info)

    return JsonResponse(records_data, safe=False, status=200)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_detection_records_by_api(request):
    app_id = request.query_params.get('app_id')
    if not app_id:
        return JsonResponse({'error': 'Missing target application ID'}, status=400)

    try:
        target_app = TargetApplication.objects.get(id=app_id, user=request.user)
    except TargetApplication.DoesNotExist:
        return JsonResponse({'error': 'Target application not found or you do not have permission'}, status=404)

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

    return JsonResponse(traffic_data_list, safe=False, status=200)
