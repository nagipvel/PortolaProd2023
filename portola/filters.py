from rest_framework import viewsets
import rest_framework_filters as filters
# from rest_framework.filters import OrderingFilter as OrderingFilter
# import django_filters
from .models import *
from rest_framework_tracking.models import APIRequestLog

class DocumentFilter(filters.FilterSet):
    project = filters.RelatedFilter('ProjectFilter', field_name='project', queryset=Project.objects.all())
    entity = filters.RelatedFilter('EntityFilter', field_name='entity', queryset=Entity.objects.all())
    tags = filters.RelatedFilter('TagFilter', field_name='technology_tags', queryset=TechnologyTag.objects.all())
    issued_min = filters.DateFilter(lookup_expr='gte', field_name='issued_date')
    issued_max = filters.DateFilter(lookup_expr='lte', field_name='issued_date')

    class Meta:
        model = Document
        fields = {
            'project': ['exact'],
            'type':['exact','in'],
            'title':['exact','icontains'],
            'entity':['exact'],
            'tags': ['exact'],
            'disclosure':['exact','in'],
            'issued_min':['exact'],
            'issued_max':['exact'],
        }

class EntityFilter(filters.FilterSet):
    class Meta:
        model = Entity
        fields = {
            'id': ['exact','in'],
            'type': ['exact','icontains'],
            'legal_name': ['exact','icontains'],
        }

class LogFilter(filters.FilterSet):
    requested_min = filters.DateFilter(lookup_expr='gte', field_name='requested_at')
    requested_max = filters.DateFilter(lookup_expr='lte', field_name='requested_at')
    user = filters.RelatedFilter('UserFilter', field_name='user', queryset=User.objects.all())

    class Meta:
        model = APIRequestLog
        fields = {
            'user':['exact'],
            # 'username':['icontains'],
            'path':['icontains'],
            'status_code':['exact'],
            'requested_min':['exact'],
            'requested_max':['exact'],
        }

class NotificationFilter(filters.FilterSet):
    queued_min = filters.DateFilter(lookup_expr='gte', field_name='queued_date')
    queued_max = filters.DateFilter(lookup_expr='lte', field_name='queued_date')
    recipient = filters.RelatedFilter('UserFilter', field_name='recipient', queryset=User.objects.all())

    class Meta:
        model = NotificationQueue
        fields = {
            'recipient':['exact'],
            'subject':['icontains'],
            'queued_min':['exact'],
            'queued_max':['exact'],
        }

class ProjectFilter(filters.FilterSet):
    class Meta:
        model = Project
        fields = {
            'status': ['exact'],
            'number': ['exact','in'],
            'customer':['exact']
        }

class RequestFilter(filters.FilterSet):
    # This is how I'd like to use ordering:
    # expires = filters.RelatedFilter('SortFilter', field_name='expires', queryset=Request.objects.all())

    class Meta:
        model = Request
        fields = {
            'status': ['exact','in'],
            'expires': ['exact']
        }

class TagFilter(filters.FilterSet):
    class Meta:
        model = TechnologyTag
        fields = {
            'id': ['exact','in'],
            'title': ['exact','in'],
        }

class ProfileFilter(filters.FilterSet):
    entity = filters.RelatedFilter('EntityFilter', field_name='entity', queryset=Entity.objects.all())

    class Meta:
        model = Profile
        fields = {
            'entity': ['exact','in'],
        }

class UserFilter(filters.FilterSet):
    profile = filters.RelatedFilter('ProfileFilter', field_name='profile', queryset=Profile.objects.all())

    class Meta:
        model = User
        fields = {
            'email': ['exact','icontains'],
            'profile':['exact']
            }
