# models.py
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, MaxValueValidator, URLValidator, RegexValidator


class User(AbstractUser):
    email = models.EmailField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.username


class PathSegment(models.Model):
    name = models.CharField(max_length=50)
    is_path_variable = models.BooleanField()

    def __str__(self):
        return self.name


class RequestParam(models.Model):
    name = models.CharField(max_length=50)
    is_necessary = models.BooleanField()

    def __str__(self):
        return self.name


class RequestDataField(models.Model):
    TYPE_CHOICES = (
        ('String', 'String'),
        ('Number', 'Number'),
        ('Boolean', 'Boolean'),
        ('List', 'List'),
        ('Object', 'Object'),
    )
    name = models.CharField(max_length=50)
    type = models.CharField(max_length=10, choices=TYPE_CHOICES)

    def __str__(self):
        return self.name


class API(models.Model):
    METHOD_CHOICES = (
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
    )
    sample_url = models.CharField(max_length=200, validators=[URLValidator()])
    sample_request_data = models.CharField(max_length=200)
    request_method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    function_description = models.CharField(max_length=200)
    permission_info = models.CharField(max_length=2000)
    path_segment_list = models.ManyToManyField(PathSegment)
    request_param_list = models.ManyToManyField(RequestParam)
    request_data_fields = models.ManyToManyField(RequestDataField)

    def __str__(self):
        return f"API - {self.request_method} {self.sample_url}"


class LoginCredential(models.Model):
    user_role = models.CharField(max_length=20)
    username = models.CharField(max_length=50)
    password = models.CharField(max_length=100)

    def __str__(self):
        return f"{self.user_role} - {self.username}"


class DetectFeature(models.Model):
    name = models.CharField(max_length=20)
    description = models.CharField(max_length=100)

    def __str__(self):
        return self.name


def validate_string_list(value):
    return all(isinstance(s, str) and 1 <= len(s) <= 100 for s in value) and len(value) > 0


class SeqOccurTimeFeature(DetectFeature):
    string_list = models.JSONField(validators=[validate_string_list])

    def __str__(self):
        return f"SeqOccurTimeFeature - {self.name}"


class TargetApplication(models.Model):
    APP_name = models.CharField(max_length=20, unique=True)
    APP_url = models.CharField(max_length=200, validators=[URLValidator()])
    user_behavior_cycle = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(100)])
    SFWAP_address = models.CharField(max_length=20,
                                     validators=[RegexValidator(r'^\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}:\d{1,5}$')])
    description = models.CharField(max_length=2000)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_credentials = models.ManyToManyField(LoginCredential)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_draft = models.BooleanField(default=False)

    last_API_discovery_at = models.DateTimeField(null=True, blank=True)
    last_model_construction_at = models.DateTimeField(null=True, blank=True)

    discovered_API_list = models.ManyToManyField(API, related_name='discovered_in_apps') # 前端需要调用get_api_lists接口以获取这两个列表的数据
    user_API_list = models.ManyToManyField(API, related_name='used_in_apps')

    DETECT_TASK_STATE_CHOICES = (
        ('BASIC_INFO_TO_CONFIGURE', 'BASIC_INFO_TO_CONFIGURE'),  # is_draft=True
        ('API_LIST_TO_DISCOVER', 'API_LIST_TO_DISCOVER'),  # is_draft=False, last_API_discovery_at=None
        ('API_LIST_TO_IMPROVE', 'API_LIST_TO_IMPROVE'),
        # is_draft=False, last_API_discovery_at!=None, last_model_construction_at=None
        ('MODEL_FEATURES_TO_CONFIGURE', 'MODEL_FEATURES_TO_CONFIGURE'),
        # is_draft=False, last_API_discovery_at!=None, last_model_construction_at!=None, 未开始检测
        ('STARTED', 'STARTED'),
        ('PAUSED', 'PAUSED')
    )
    detect_state = models.CharField(max_length=50, choices=DETECT_TASK_STATE_CHOICES)

    detect_feature_list = models.ManyToManyField(DetectFeature, related_name='used_in_apps', blank=True)

    model_report = models.TextField(null=True, blank=True)

    enhanced_detection_enabled = models.BooleanField(null=True, blank=True)
    combined_data_duration = models.IntegerField(null=True, blank=True)

    def __str__(self):
        return self.APP_name


class TrafficData(models.Model):
    METHOD_CHOICES = (
        ('GET', 'GET'),
        ('POST', 'POST'),
        ('PUT', 'PUT'),
        ('DELETE', 'DELETE'),
    )
    method = models.CharField(max_length=10, choices=METHOD_CHOICES)
    header = models.CharField(max_length=5000)
    url = models.CharField(max_length=1000)
    data = models.CharField(max_length=5000)
    status_code = models.IntegerField()
    accessed_at = models.DateTimeField()
    API = models.ForeignKey(API, on_delete=models.SET_NULL, null=True, blank=True)

    DETECTION_RESULT_CHOICES = (
        ('NORMAL', 'NORMAL'),
        ('MALICIOUS', 'MALICIOUS'),
    )
    detection_result = models.CharField(max_length=20, choices=DETECTION_RESULT_CHOICES)

    class Meta:
        ordering = ['accessed_at']

    def __str__(self):
        return f"TrafficData - {self.method} {self.url}"


class DetectionRecord(models.Model):
    DETECTION_RESULT_CHOICES = (
        ('ALLOW', 'ALLOW'),
        ('ALARM', 'ALARM'),
        ('INTERCEPTION', 'INTERCEPTION'),
    )
    app = models.ForeignKey(TargetApplication, on_delete=models.CASCADE)
    started_at = models.DateTimeField()
    ended_at = models.DateTimeField()
    traffic_data_list = models.ManyToManyField(TrafficData)
    detection_result = models.CharField(max_length=20, choices=DETECTION_RESULT_CHOICES)

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.traffic_data_list.count() == 0:
            raise ValidationError("traffic_data_list cannot be empty.")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"DetectionRecord - {self.app.APP_name} ({self.started_at} - {self.ended_at})"
