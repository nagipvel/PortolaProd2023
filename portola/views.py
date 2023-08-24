#from django.shortcuts import render
import json
from datetime import datetime, timedelta
from django.db.models import Q
from django.contrib.auth.models import User
from django.utils import timezone
from django.http import FileResponse, HttpResponse
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.exceptions import ObjectDoesNotExist
from .models import *
from .serializers import *
from .permissions import *
from .filters import *
from .email import *
from .EmptyNone import *
from .authentication import token_expire_handler, expires_in, token_refresh
from .utils import decrypt, encrypt
from rest_framework import permissions
from rest_framework import generics
from rest_framework import renderers
from rest_framework import viewsets
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.parsers import FileUploadParser
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework_tracking.mixins import LoggingMixin, BaseLoggingMixin
from rest_framework_tracking.models import APIRequestLog
from rest_framework_extensions.mixins import DetailSerializerMixin
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.status import (
    HTTP_400_BAD_REQUEST,
    HTTP_404_NOT_FOUND,
    HTTP_200_OK,
)
from rest_framework.response import Response

from openpyxl import Workbook
from openpyxl.utils.dataframe import dataframe_to_rows
from openpyxl.writer.excel import save_virtual_workbook
from io import BytesIO
import pandas as pd


DAYS_NEW=30

@api_view(["POST"])
@permission_classes((AllowAny,))  # here we specify permission by default we set IsAuthenticated
def signin(request):
    # try usernames first
    signin_serializer = UserSigninSerializer(data = request.data)
    if not signin_serializer.is_valid():
        # bad request or just a token?
        signin_serializer = TokenSigninSerializer(data = request.data)
        if not signin_serializer.is_valid():
            # I have nno idea what you're asking
            return Response(signin_serializer.errors, status = HTTP_400_BAD_REQUEST)
        else:
            # we have a token
            original_token = decrypt(signin_serializer.data['token'])
            try:
                token = Token.objects.get(key = original_token)
            except Token.DoesNotExist:
                raise AuthenticationFailed("Invalid token.")
            token = token_refresh(token)
            user = User.objects.get(username=token.user)
            # print(user)
    else:
        user = authenticate(
            username = signin_serializer.data['username'],
            password = signin_serializer.data['password']
        )
        # user = User.objects.get(username = user)


    if not user:
        return Response({'detail': 'Invalid credentials or activate account.'}, status=HTTP_404_NOT_FOUND)

    #TOKEN STUFF
    token, _ = Token.objects.get_or_create(user = user)

    #token_expire_handler will check, if the token is expired it will generate new one
    is_expired, token = token_expire_handler(token)
    # user_serialized = UserSerializer(data=user)
    # print(request.data)
    # if user_serialized.is_valid():
    return Response({
        'user': user.username,
        'id':user.id,
        'expires_in': expires_in(token),
        'token': token.key
    }, status=HTTP_200_OK)

@api_view(["POST"])
@permission_classes((AllowAny,))
def forgot_password(request):
    forgot_serializer = ForgotPasswordSerializer(data = request.data)
    if forgot_serializer.is_valid():
        try:
            user = User.objects.get(username=forgot_serializer.data['username'])
        except ObjectDoesNotExist:
            return Response({
                    'status':'User {0} not found.'.format(forgot_serializer.data['username'])
                }, status=status.HTTP_400_BAD_REQUEST)

        token, _ = Token.objects.get_or_create(user = user)
        note = Notification()
        note.throttled_email(template='reset_password',
            username = user.username,
            magic_link =  settings.CLIENT_HOST + '/forgot_password/' + encrypt(token))
        return Response({
            'status': 'Password reset link sent to {0}.'.format(user.email),
        }, status=status.HTTP_200_OK)

@api_view(["GET"])
def user_info(request):
    return Response({
        'user': request.user.username,
        'expires_in': expires_in(request.auth)
    }, status=HTTP_200_OK)

@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'profiles': reverse('profile-list', request=request, format=format),
        'projects': reverse('project-list', request=request, format=format),
        'users': reverse('user-list', request=request, format=format),
        'documents': reverse('document-list', request=request, format=format),
        'entities': reverse('entity-list', request=request, format=format),
        'tags': reverse('tag-list', request=request, format=format),
    })

class ApiRequestLogViewSet(DetailSerializerMixin, viewsets.ModelViewSet):
    """
    Filters:
    ?path=
    ?path__icontains=

    requested_at has date range filters:
    `?requested_min=2018-01-01`
    `?requested_max=2018-12-31`
    of course, chain them for a full range: `?issued_min=2018-01-01&issued_max=2018-12-31`
    """
    queryset = APIRequestLog.objects.all()
    serializer_class = ApiRequestLogSerializer
    permission_classes = [IsSuperUser,]
    serializer_detail_class = ApiRequestLogDetailSerializer
    filter_class = LogFilter

class BinaryFileRenderer(renderers.BaseRenderer):
    '''
    taken from http://www.vhinandrich.com/fix-django-rest-framework-tracking-drf-tracking-errors-django-model-filefield
    as a download renderer
    '''
    media_type = 'application/octet-stream'
    format = 'binary'
    charset = None
    render_style = 'binary'

    def render(self, data, media_type=None, renderer_context=None):
        return data

class BootstrapViewSet(viewsets.ViewSet):
    """
    This vewset provides lists to the UI
    """
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]

    def list(self, request):
        dataset = {}

        dataset['CO_ENTITY_TYPES'] = dict(CO_ENTITY_TYPES)
        dataset['DOCUMENT_VISIBILITY'] = dict(DOCUMENT_VISIBILITY)
        dataset['DOCUMENT_TYPE'] = dict(DOCUMENT_TYPE)
        dataset['ENTITY_TYPES'] = dict(ENTITY_TYPES)
        dataset['PRODUCT_TYPES'] = dict(PRODUCT_TYPES)
        dataset['PROJECT_CHOICES'] = dict(PROJECT_CHOICES)
        dataset['TAG_TYPES'] = dict(TAG_TYPES)
        dataset['SETTINGS'] = {"session":"600"}
        dataset['HOST'] = settings.ALLOWED_HOSTS
        return Response(dataset)

class CompanyViewSet(LoggingMixin, viewsets.ModelViewSet):
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Company.objects.all()

    serializer_class = CompanySerializer
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]

    # permissions incorrect
    # admin for POST/PUT/PATCH
    # authenticated for view`

class DocumentViewSet(
    # TransferEmptyNoneMixin,
    LoggingMixin, viewsets.ModelViewSet):
    """
    Filters:
    `?entity__type={str}`
    `?entity__legal_name={str}`
    `?entity__legal_name__icontains={str}`
    `?project__number={str}`
    `?project__status=[ACTIVE|INACTIVE]`
    `?title={str}`
    `?title__icontains={str}` case INSENSITIVE substring search
    `?type=[Doctypes]` Check filters for doctypes
    `?disclosure={str}`
    `?disclosure__in={csv}` comma separated values

    issued_date has date range filters:
    `?issued_min=2018-01-01`
    `?issued_max=2018-12-31`
    of course, chain them for a full range: `?issued_min=2018-01-01&issued_max=2018-12-31`

    Tags are special. they use the `in` filter to allow for more sphisticated queries.
    `?tags__title__in=1000V`
    will filter down to all ducuments with the 1000V tag. comma separated lists are OR:
    ?tags__title__in=300W,260W Also: ?tags__id__in=2,4,6 uses tags id

    Complex filters allow for use of AND:
    (tags__title__in=1000V)&(tags__title__in=280W,300W) would filter doc with 1000V AND either 280W OR 300W

    Complex filters need urlencoding:
    ?filters=%28tags__title__in%253D1000V%29%26%28tags__title__in%253D260W%29
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE','GET']
    queryset = Document.objects.all()
    parser_class = (FileUploadParser,)
    serializer_class = DocumentSerializer
    filter_class = DocumentFilter
    # filter_backends = [filters.OrderingFilter,RestFrameworkFilterBackend]
    ordering_fields = '__all__'
    empty_to_none_fields = ("factory_witness_date",)

    # permission_classes need to be updated to allow view
    # if:
    #    generally available
    #    available for request
    #    Owned by the current entity
    permission_classes = (IsAvailableOrAgreed|IsStaff,)
    def get_serializer_context(self):
        return {'request': self.request}

    def should_log(self, request, response):
        # need to override the logging here so that we ONLY log GET for /download
        if ( request.method == 'GET'):
            if ('download' in request.path):
                return (True)
            else:
                return (False)
        else:
            return self.logging_methods == '__all__' or request.method in self.logging_methods

    # def perform_create(self, serializer):
    #     # TODO: This should be either changed to the correct user, or
    #     # we need to make sure that the owner entity is correct
    #     serializer.save(owner=self.request.user)

    # Override _clean_data to decode data with ignore instead of replace to ignore
    # errors in decode so when the logger inserts the data to db, it will not hit
    # any decoding/encoding issues
    def _clean_data(self, data):
        if isinstance(data, bytes):
            # data = data.decode(errors='ignore')
            data = 'CLEANED FILE DATA'
        return super(DocumentViewSet, self)._clean_data(data)

    @action(detail=False, methods=['get','post'],
        permission_classes=(permissions.IsAuthenticated,IsAvailableOrAgreed),)
    def batch(self, request):
        self.context={'request':request}
        if request.method == 'POST':
            response ={}
            docrequest = {}
            params = json.loads(request.body)
            for action in params.keys():
                queryset = Document.objects.get(id=int(action))
                docrequest['requestor'] = request.user.pk
                docrequest['document'] = int(action)
                docrequest['status'] = 'ACTIVE'
                docrequest['requestor_comment'] = params[action]
                serializer = DocRequestSerializer(data=docrequest, many=False, context=self.context)
                if (serializer.is_valid()):
                    serializer.save()
                    response[action] = params[action]
            return Response(response)
        else: # GET
            queryset = []
        serializer = DocumentSerializer(queryset, many=True, context=self.context)
        return Response(serializer.data)

    @action(detail=True, methods=['get'],
        # renderer_classes=(BinaryFileRenderer,),
        permission_classes=(IsAvailableOrAgreed|IsStaff,),
        )
    def download(self, request, pk=None):
        queryset = Document.objects.get(id=pk)
        documentFile = queryset.file
        file_handle = documentFile.open()
        # send file TODO: Not all files are PDF
        self.check_object_permissions(self.request, queryset)
        # response = FileResponse(file_handle)
        response = HttpResponse(file_handle, content_type='application/pdf')
        response['Content-Disposition'] = 'attachment; filename={0}'.format(documentFile)
        return response

    # using IsAvailableOrAgreed here because it's not the download link
    @action(detail=True, methods=['get','post'],
        permission_classes=(IsAvailableOrAgreed,),
        serializer_class=RequestSerializer)
    def docrequest(self, request, pk=None):
        self.context={'request':request}
        queryset = Document.objects.get(id=pk)
        params = {}
        docrequest = {}

        # check for a current request

        if request.method == 'POST':
            docrequest['requestor'] = request.user.pk
            docrequest['document'] = queryset.pk
            docrequest['status'] = 'ACTIVE'

            try:
                # This won't handle an ampty JSON object. requires {'requestor_comment':'foo'}
                params = json.loads(request.body)
                docrequest['requestor_comment'] = params['requestor_comment']
            except Exception as e:
                docrequest['requestor_comment'] = request.POST['requestor_comment']

            serializer = DocRequestSerializer(data=docrequest, many=False, context=self.context)
            if (serializer.is_valid()):
                serializer.save()
                return Response(True) # I would rather return a data object here...
            else:
                return Response(serializer.errors)
        if request.method == 'GET':
            serializer = DocumentSerializer(queryset, many=False, context=self.context)
        # serializer = RequestSerializer(queryset, many=False, context=self.context)
        return Response(serializer.data)

    # using IsAvailableOrAgreed here because it's not the download link
    @action(detail=True, methods=['get','post'],
        permission_classes=(IsProjectApprover|IsSuperUser,),
        serializer_class=DocumentDisclosureSerializer)
    def disclose(self, request, pk=None):
        disclose = {}
        params ={}
        self.context={'request':request}
        queryset = Document.objects.get(id=pk)
        if request.method == 'POST':
            if queryset.disclosure == 'PENDING':
                try:
                    # print('IN TRY')
                    # print(request.body)
                    # This is broken for form input
                    params = json.loads(request.body)
                    # disclose['id'] = queryset.pk
                    disclose['disclosure'] = params['disclosure']
                    disclose['disclosure_date'] = timezone.now().date()
                except Exception as e:
                    print(e)
                    pass
            serializer = DocumentDisclosureSerializer(data=disclose, many=False, context=self.context)
            if (serializer.is_valid()):
                serializer.update(queryset,serializer.validated_data)
                return Response(True) # I would rather return a data object here...
            else:
                return Response(serializer.errors)
        if request.method == 'GET':
            serializer = DocumentSerializer(queryset, many=False, context=self.context)
        # serializer = RequestSerializer(queryset, many=False, context=self.context)
        # This is where we want to notify followers of a project that there
        # is a new report available to request or download
        # notification = Notification(type='followers', template='new_document')
        # notification.send()
        return Response(serializer.data)

    @action(detail=False, methods=['get'])
    def entities(self, request, pk=None):
        entities = Entity.objects.filter((Q(type='MANUFACTURER') & Q(public=True))|Q(pk=request.user.profile.entity.id))
        entity_list = []
        for entity in entities:
            if entity.document_set.count() > 0:
                entity_list.append({"id":entity.id , "displayName": entity.display_name})
        return Response(entity_list)

    @action(detail=False, methods=['get'])
    def new(self, request, pk=None):
        self.context={'request':request}
        new_days = datetime.today() - timedelta(days=DAYS_NEW)
        # MFG users get a count of their new reports:
        if self.request.user.profile.entity.type == 'MANUFACTURER':
            new_count = Document.objects.filter(entity=self.request.user.profile.entity).filter(issued_date__gte=new_days).count()
            content = {'new_count': new_count}
        # DSP/DSC Users get the newest reports:
        else:
            qs = self.get_queryset().filter(issued_date__gte=new_days)[:5]
            serializer = DocumentDashboardSerializer(qs, many=True, context=self.context)
            content = serializer.data
        return Response(content)

    @action(detail=False, methods=['get'])
    def pending(self, request, pk=None):
        pending_count = Document.objects.filter(entity=self.request.user.profile.entity).filter(disclosure='PENDING').count()
        content = {'pending_count': pending_count}
        return Response(content)

    @action(detail=False, methods=['get'])
    def projects(self, request, pk=None):
        documents = self.get_queryset().order_by('project__number')
        projects = []
        for document in documents:
            try:
                # KLUGE: Some test data missing proper entities.
                if document.project.number not in projects:
                    projects.append(document.project.number)
            except:
                print(document)
        return Response(projects)

    @action(detail=False, methods=['get'])
    def range(self, request, pk=None):
        documents = self.get_queryset().order_by('issued_date')
        range = {}
        range['issued_min'] = documents.first().issued_date
        range['issued_max'] = documents.last().issued_date
        return Response(range)

    # placeholder
    @action(detail=False, methods=['get'])
    def types(self, request, pk=None):
        doctypes = dict(DOCUMENT_TYPE)
        documents = self.get_queryset().order_by('type')
        types = {}
        for document in documents:
            try:
                types[document.type] = doctypes[document.type]
            except:
                print(document)
        return Response(types)


    def get_queryset(self):
        order = tuple(self.request.GET.get('ordering','issued_date').split(','))
        # print(order)
        try:
            if self.request.user.profile.entity.type == 'MANUFACTURER':
                result = (
                    Document.objects.filter(entity=self.request.user.profile.entity ).order_by(*order)
                    )
            elif self.request.user.is_staff:
                # result = (Document.objects.all().order_by(order))
                result = (Document.objects.all().order_by(*order))
            else:
                result = (
                    Document.objects.filter(disclosure='BY REQUEST') |
                    Document.objects.filter(disclosure='GENERAL') |
                    Document.objects.filter(entity=self.request.user.profile.entity )
                    ).distinct().order_by(*order)
            return result
        except Exception as e:
            return Document.objects.none()

class EntityViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.

    Filters:
    `/api/entities/?type=[]`
    `legal_name={str}`
    `legal_name__icontains={str}`
    Types:
        ['PARTNER','CLIENT','MANUFACTURER','PVEL']

    Batch mode:
    {
    "1":"FOLLOW",
    "2":"UNFOLLOW"
    }
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Entity.objects.all()
    serializer_class = EntityListSerializer
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]
    filter_class = EntityFilter

    @action(detail=False, methods=['get','post'],serializer_class=EntitySerializer,
    permission_classes=[permissions.IsAuthenticated,],)
    def batch(self, request):
        self.context={'request':request}
        # print(request.body)
        if request.method == 'POST':
            response ={}
            params = json.loads(request.body)
            for action in params.keys():
                queryset = Entity.objects.get(id=int(action))
                if params[action] == "FOLLOW":
                    if request.user not in queryset.followers.all():
                        queryset.followers.add(request.user)
                        queryset.save()
                        response[action] = params[action]
                if params[action] == "UNFOLLOW":
                    if request.user in queryset.followers.all():
                        queryset.followers.remove(request.user)
                        queryset.save()
                        response[action] = params[action]
            return Response(response)
        else:
            queryset = self.get_queryset()
        # need to create a queryset to use this here:
        serializer = EntitySerializer(queryset, many=True, context=self.context)
        return Response(serializer.data)

    @action(detail=True, methods=['get','post'], serializer_class=EntityFollowSerializer,
        permission_classes=[permissions.IsAuthenticated,],)
    def follow(self, request, pk=None):
        queryset = Entity.objects.get(id=pk)
        self.context={'request':request}
        if request.method == 'POST' and request.user not in queryset.followers.all():
            queryset.followers.add(request.user)
            queryset.save()
        serializer = EntityFollowSerializer(queryset, many=False, context=self.context)
        return Response(serializer.data)

    @action(detail=True, methods=['get','post'], serializer_class=EntityFollowSerializer,
        permission_classes=[permissions.IsAuthenticated,],)
    def unfollow(self, request, pk=None):
        queryset = Entity.objects.get(id=pk)
        self.context={'request':request}
        if request.method == 'POST' and request.user in queryset.followers.all():
            queryset.followers.remove(request.user)
            queryset.save()
        serializer = EntityFollowSerializer(queryset, many=False, context=self.context)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(created_by=self.request.user)

    # test limited view for list:
    def retrieve(self, request, pk=None ):
        self.context={'request':request}
        queryset = Entity.objects.get(id=pk)
        serializer = EntitySerializer(queryset, many=False, context=self.context)
        return Response(serializer.data)

    # entity visibility:
    # MFGs see all DSPs and DSCs
    # DSPs see everyone
    def get_queryset(self):
        # print('IN HERE')
        result = Entity.objects.all()
        if self.request.user.is_superuser:
            return result

        result = result.filter(public=True)

        if self.request.user.profile.entity.type in ['MANUFACTURER']:
            result = result.filter(type__in=['PVEL','PARTNER','CLIENT'])
        return result


class FaqViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.

    type should be set to the intended audience, with PVEL being the choice for "Both"

    Text needs to be formatted using markdown, via showdown.js. Test the look of your
    formatting as it will appear in the site here: http://demo.showdownjs.com/
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Faq.objects.all()
    # queryset = Faq.objects.filter(IsEntityTypeFilterBackend)
    serializer_class = FaqSerializer
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, last_updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(last_updated_by=self.request.user, last_updated=timezone.now())

    def get_queryset(self):
        if self.request.user.profile.entity.type in ['MANUFACTURER','CLIENT']:
            result = Faq.objects.filter(type=self.request.user.profile.entity.type) | Faq.objects.filter(type='PVEL')
        else:
            result = Faq.objects.all()
        return result

class NewsFeedViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    This viewset automatically provides `list` and `detail` actions.

    type should be set to the intended audience, with PVEL being the choice for "Both"

    Text needs to be formatted using markdown, via showdown.js. Test the look of your
    formatting as it will appear in the site here: http://demo.showdownjs.com/

    Permissions:
        [permissions.IsAuthenticated,IsAdminOrReadOnly]

        All logged in users can read
        All Admin users can read and write

    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = NewsFeed.objects.all()
    # queryset = Faq.objects.filter(IsEntityTypeFilterBackend)
    serializer_class = NewsFeedSerializer
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user, last_updated_by=self.request.user)

    def perform_update(self, serializer):
        serializer.save(last_updated_by=self.request.user, last_updated=timezone.now())

    def get_queryset(self):
        # This logic is for a different newsfeed style.
        # if self.request.user.profile.entity.type in ['MANUFACTURER','CLIENT',]:
        #     result = NewsFeed.objects.filter(type=self.request.user.profile.entity.type) | NewsFeed.objects.filter(type='PVEL')
        # else:
        #     result = NewsFeed.objects.all()
        result=[]
        if self.request.user.profile.entity.type in ['PVEL',]:
            result = NewsFeed.objects.all()
        else:
            result.append(NewsFeed.objects.filter(type=self.request.user.profile.entity.type).last())
        return result

class NotificationViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    Quick and dirty debugging queue
    Filters:
            'recipient':['exact,icontains'],
            'subject':['icontains'],
            'queued_min':['exact'],
            'queued_max':['exact'],
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = NotificationQueue.objects.all()
    serializer_class = NotificationQueueSerializer
    permission_classes = [IsSuperUser,]
    filter_class = NotificationFilter

    @action(detail=True, methods=['get','post'],
        serializer_class=ResendNotificationSerializer,
        permission_classes=[IsSuperUser,],)
    def resend(self, request, pk=None):
        note = NotificationQueue.objects.get(pk=pk)
        serializer = ResendNotificationSerializer(data=request.data)
        if serializer.is_valid():
            user = authenticate(
                username = request.user.username,
                password = serializer.data['password']
            )
            if user:
                resend = Notification()
                resend.throttled_email(
                    resend = True,
                    original_msg = note,
                )
                return Response({'status' :'Message {0} resent'.format(pk)
                    }, status=status.HTTP_200_OK)
        return Response(serializer.errors,
            status=status.HTTP_401_UNAUTHORIZED)

class ProfileCreateView(LoggingMixin, generics.ListCreateAPIView):
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,
    #                       IsOwnerOrAdmin)
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    serializer_class = ProfileSerializer
    queryset = Profile.objects.all()
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]


class ProfileViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    Permissions:
        [permissions.IsAuthenticated,IsAdminOrReadOnly]
        All authenticated users can read_only
        allAdmins can read and write

    We may want to change the permissions here so that a user can make
    chenges to their own user profile information

    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Profile.objects.all()
    serializer_class = ProfileSerializer
    # This might be wrong, we may want to give the user the opportunity to
    # update their own user profile information
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

class ProjectViewSet(DetailSerializerMixin, LoggingMixin, viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]

    Should look at this more to determine if there are user classes that we want
    to prevent from seeing projects. Do MFGs only see their own projects?

    Filtering:
    `/api/projects/?status=ACTIVE`
    `/api/projects/?status=INACTIVE`
    `/api/projects/?number={str}`
    `/api/projects/?customer={id}` where id is an entity id
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Project.objects.all()
    # serializer_class = ProjectListSerializer
    serializer_detail_class =  ProjectSerializer
    serializer_class =  ProjectSerializer
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]
    filter_class = ProjectFilter

    @action(detail=False, methods=['get'], filter_class=ProjectFilter)
    def count(self, request, pk=None):
        project_count = Project.objects.filter(customer=self.request.user.profile.entity).count()
        content = {'project_count': project_count}
        return Response(content)

    # This override is disabled for the moment
    # def get_queryset(self):
    def get_queryset(self):
        order = tuple(self.request.GET.get('ordering','number').split(','))

        if self.request.user.profile.entity.type in ['MANUFACTURER','CLIENT']:
            result = Project.objects.filter(customer=self.request.user.profile.entity).order_by(*order)
        else:
            result = Project.objects.all().order_by(*order)
        return result

    @action(detail=False, methods=['get'], filter_class=ProjectFilter)
    def numbers(self, request, pk=None):
        queryset = self.get_queryset()
        self.context={'request':request}
        serializer = ProjectNumberSerializer(queryset, many=True, context=self.context)
        return Response(serializer.data)
        # super.list(self, request)

    @action(detail=False, methods=['get','post'],serializer_class=ProjectSerializer,
        permission_classes=[permissions.IsAuthenticated,],)
    def batch(self, request):
        self.context={'request':request}
        if request.method == 'POST':
            response ={}
            params = json.loads(request.body)
            for action in params.keys():
                queryset = Project.objects.get(id=int(action))
                if params[action] == "FOLLOW":
                    if request.user not in queryset.followers.all():
                        queryset.followers.add(request.user)
                        queryset.save()
                        response[action] = params[action]
                if params[action] == "UNFOLLOW":
                    if request.user in queryset.followers.all():
                        queryset.followers.remove(request.user)
                        queryset.save()
                        response[action] = params[action]
            return Response(response)
        else:
            queryset = self.get_queryset()
        # need to create a queryset to use this here:
        serializer = ProjectSerializer(queryset, many=True, context=self.context)
        return Response(serializer.data)

    @action(detail=True, methods=['get','post'], serializer_class=ProjectFollowSerializer,
        permission_classes=[permissions.IsAuthenticated,],)
    def follow(self, request, pk=None):
        queryset = Project.objects.get(id=pk)
        self.context={'request':request}
        if request.method == 'POST' and request.user not in queryset.followers.all():
            queryset.followers.add(request.user)
            queryset.save()
        serializer = ProjectFollowSerializer(queryset, many=False, context=self.context)
        return Response(serializer.data)

    @action(detail=True, methods=['get','post'], serializer_class=ProjectFollowSerializer,
        permission_classes=[permissions.IsAuthenticated,],)
    def unfollow(self, request, pk=None):
        queryset = Project.objects.get(id=pk)
        self.context={'request':request}
        if request.method == 'POST' and request.user in queryset.followers.all():
            queryset.followers.remove(request.user)
            queryset.save()
        serializer = ProjectFollowSerializer(queryset, many=False, context=self.context)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()

class PVModelViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    This viewset s for cerating and execuiting PV modeling experiments
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]

    Currntly disabled and only for experimentation
    """
    logging_methods =  ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = PVModel.objects.all()
    serializer_class = PVModelSerializer
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]

    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user)

    @action(detail=True, methods=['get'], renderer_classes=(BinaryFileRenderer,))
    def runmodel(self, request, pk=None):
        queryset = Document.objects.get(id=pk)
        documentFile = queryset.file
        file_handle = documentFile.open()
        # send file
        response = FileResponse(file_handle)
        return response

class RequestViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.

    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]

    Filters:
    `?status={str}`
    `?status__in={csv}`

    Batch mode:
    ```
    {
    "1":"APPROVED",
    "2":"REFUSED"
    }

    ```
    Where the first key is the ID of the request to process, and the value is the process to follow.
    """
    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = Request.objects.all()
    serializer_class = RequestSerializer
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]
    filter_class = RequestFilter

    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    # Approve and reject are only allowed for the document approver for that
    # PROJECT
    @action(detail=True, methods=['get','post'], serializer_class=DocRequestSerializer,
        permission_classes=[permissions.IsAuthenticated,IsProjectApprover],)
    def approve(self, request, pk=None):
        queryset = Request.objects.get(id=pk)
        requested_doc = Document.objects.get(id=queryset.document.id)
        self.context={'request':request}
        if request.method == 'POST':
            if (not queryset.requestor.profile.entity in requested_doc.permitted_entities.all()):
                requested_doc.permitted_entities.add(queryset.requestor.profile.entity)
            queryset.status = 'APPROVED'
            queryset.resolved = timezone.now().date()
            queryset.save()
        serializer = RequestSerializer(queryset, many=False, context=self.context)
        return Response(serializer.data)

    # This is for new requests that the entity has made (DSP/DSC users).
    @action(detail=False, methods=['get'], serializer_class=RequestNewSerializer)
    def new(self, request, pk=None):
        self.context={'request':request}
        new_qs = self.get_queryset()[:5]
        serializer = RequestNewSerializer(new_qs, many=True, context=self.context)
        return Response(serializer.data)

    @action(detail=False, methods=['get','post'],serializer_class=DocRequestSerializer,
        permission_classes=[permissions.IsAuthenticated,],)
    def batchapprove(self, request, pk=None):
        queryset = Request.objects.all()
        self.context={'request':request}
        # print(request.body)
        if request.method == 'POST':
            response ={}
            params = json.loads(request.body)
            for action in params.keys():
                queryset = Request.objects.get(id=int(action))
                requested_doc = Document.objects.get(id=queryset.document.id)
                # this skips IDs that the user doesn't have access to update:
                if request.user == queryset.document.project.document_approver:
                    if (not queryset.requestor.profile.entity in requested_doc.permitted_entities.all()):
                        requested_doc.permitted_entities.add(queryset.requestor.profile.entity)
                    queryset.approver_comment = params[action]
                    queryset.status = 'APPROVED'
                    queryset.resolved = timezone.now().date()
                    queryset.save()
                    response[action] = params[action]
            return Response(response)
        serializer = RequestBatchSerializer(queryset, many=False, context=self.context)
        return Response(serializer.data)

    @action(detail=False, methods=['get','post'],serializer_class=DocRequestSerializer,
        permission_classes=[permissions.IsAuthenticated,],)
    def batchreject(self, request, pk=None):
        queryset = Request.objects.all()
        self.context={'request':request}
        # print(request.body)
        if request.method == 'POST':
            response ={}
            params = json.loads(request.body)
            for action in params.keys():
                queryset = Request.objects.get(id=int(action))
                requested_doc = Document.objects.get(id=queryset.document.id)
                # this skips IDs that the user doesn't have access to update:
                if request.user == queryset.document.project.document_approver:
                    queryset.approver_comment = params[action]
                    queryset.status = 'REFUSED'
                    queryset.resolved = timezone.now().date()
                    queryset.save()
                    response[action] = params[action]
            return Response(response)
        serializer = RequestBatchSerializer(queryset, many=False, context=self.context)
        return Response(serializer.data)


    @action(detail=False, methods=['get','post'],serializer_class=DocRequestSerializer,
        permission_classes=[permissions.IsAuthenticated,IsProjectApprover],)
    def batch(self, request, pk=None):
        queryset = Request.objects.all()
        self.context={'request':request}
        # print(request.body)
        if request.method == 'POST':
            response ={}
            params = json.loads(request.body)
            for action in params.keys():
                queryset = Request.objects.get(id=int(action))
                requested_doc = Document.objects.get(id=queryset.document.id)
                # this skips IDs that the user doesn't have access to update:
                if request.user == queryset.document.project.document_approver:
                    if params[action] == 'APPROVED':
                        if (not queryset.requestor.profile.entity in requested_doc.permitted_entities.all()):
                            requested_doc.permitted_entities.add(queryset.requestor.profile.entity)
                    queryset.status = params[action]
                    queryset.resolved = timezone.now().date()

                    queryset.save()
                    response[action] = params[action]
            return Response(response)
        serializer = RequestBatchSerializer(queryset, many=False, context=self.context)
        return Response(serializer.data)

    @action(detail=True, methods=['get','post'], serializer_class=DocRequestSerializer,
        permission_classes=[permissions.IsAuthenticated,IsProjectApprover],)
    def reject(self, request, pk=None):
        queryset = Request.objects.get(id=pk)
        self.context={'request':request}
        if request.method == 'POST':
            queryset.status = 'REFUSED'
            queryset.resolved = timezone.now().date()
            queryset.save()
        serializer = RequestSerializer(queryset, many=False, context=self.context)
        return Response(serializer.data)

    def perform_create(self, serializer):
        serializer.save()

    def get_queryset(self):
        # This only shows requests for documents my entity owns
        mydocs = Document.objects.filter(entity=self.request.user.profile.entity)
        result = (
            Request.objects.filter(document__in=mydocs) |
            Request.objects.filter(requestor=self.request.user)
        )
        return result

class TagViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    list of all technology tags.

    Filters:
    `/api/tags/?title={str}` exact match
    `/api/tags/?title__in={str}` comma separated list of tags

    """

    logging_methods = ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = TechnologyTag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [permissions.IsAuthenticated,IsAdminOrReadOnly]
    filter_class = TagFilter

class UserViewSet(LoggingMixin, viewsets.ModelViewSet):
    """
    This is the list of all users in the system.
    Permissions:
        [permissions.IsAuthenticated,IsAdminOrReadOnly]
        All authenticated users can read_only
        allAdmins can read and write

    We may want to change the permissions here so that a user can make
    changes to their own user profile information

    Also need to make sure to get the reight list permissions, currently
    all users can see everything about all the other users...

    Filters:
    `/api/users/?email={str}` exact match
    `/api/users/?email__icontains={str}` case INSENSITIVE substring match

    Ordering:
    `/api/users/?ordering=last_name` order by last name ASCENDING
    `/api/users/?ordering=-last_name` order by last name DECENDING

    Yes, that chains too: `/api/users/?ordering=-last_name&email__icontains=sun`
    """
    logging_methods =  ['POST', 'PUT', 'PATCH', 'DELETE']
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated,IsAdminOrSelf]
    filter_class = UserFilter

    @action(detail=True, methods=['put'],
        permission_classes =(IsAdminOrSelf,),
        serializer_class=PasswordSerializer)
    def set_password(self, request, pk=None):
        self.context={'request':request}
        serializer = PasswordSerializer(data=request.data)
        if serializer.is_valid():
            if not request.user.check_password(serializer.data.get('old_password')):
                return Response({'old_password': ['Wrong password.']},
                                status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            request.user.set_password(serializer.data.get('new_password'))
            request.user.save()
            token, _ = Token.objects.get_or_create(user = request.user)
            token = token_refresh(token)
            return Response({
                    'status': 'Password set.',
                    'token': token.key
                    }, status=status.HTTP_200_OK)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False,methods=['get'],
        permission_classes = [permissions.IsAdminUser,],)
    def list_users(self, request, pk=None):
        queryset = User.objects.all()
        # mdf = pd.DataFrame(data={'col1': ['foo2', 'bar'], 'col2': ['barfoo2', 'foobar']})
        mdf = pd.DataFrame(list(queryset.values(
            'username',
            'first_name',
            'last_name',
            'profile__entity__company__name',
            'profile__entity__company__website',
            'profile__entity__display_name',
            'profile__entity__legal_name',
            'profile__entity__type',
            'profile__entity__country',
        )))
        try:
            mdf.columns = [
                'UserName',
                'First Name',
                'Last Name',
                'Company Name',
                'company website',
                'Entity Name',
                'Entity Legal Name',
                'Entity Type',
                'Country'
                ]
            wb = Workbook()
            ws = wb.active
            for r in dataframe_to_rows(mdf, index=False, header=True):
                ws.append(r)
            mem_file = BytesIO(save_virtual_workbook(wb))
            # mdf.to_excel(mem_file)
            content_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            filename = 'users_file'
            response = HttpResponse(mem_file, content_type=content_type)
            response['Content-Disposition'] = f'attachment; filename={filename}.xlsx'
            return response
        except Exception as e:
            return Response({
            'status': 'Exception',
            'token': f'{e}'
            }, status=status.HTTP_200_OK)
        # self.context={'request':request}
        # serializer =UserSerializer(queryset, many=True, context=self.context)
        # return Response(serializer.data)
        return Response(mdf.to_dict(orient='records'))

    @action(detail=True, methods=['put'], serializer_class=LostPasswordSerializer)
    def lost_password(self, request, pk=None):
        self.context={'request':request}
        serializer = LostPasswordSerializer(data=request.data)
        if serializer.is_valid():
            # if not request.user.check_password(serializer.data.get('old_password')):
            #     return Response({'old_password': ['Wrong password.']},
            #                     status=status.HTTP_400_BAD_REQUEST)
            # set_password also hashes the password that the user will get
            request.user.set_password(serializer.data.get('new_password'))
            request.user.save()
            token, _ = Token.objects.get_or_create(user = request.user)
            token = token_refresh(token)
            return Response({
                    'status': 'Password set.',
                    'token': token.key
                }, status=status.HTTP_200_OK)

        return Response(serializer.errors,
                        status=status.HTTP_400_BAD_REQUEST)

    @action(detail=True, methods=['put'],
        permission_classes = [permissions.IsAdminUser,],
        serializer_class=InviteUserSerializer)
    def invite_user(self, request, pk=None):
        user = User.objects.get(pk=pk)
        self.context={'request':request}
        serializer = InviteUserSerializer(data=request.data)
        # Probably should use a permission class here
        if serializer.is_valid():
            if request.user.is_superuser:
                invite = username=serializer.data.get('username')
                if invite != user.username:
                    return Response({
                        'status': 'invitation failed. User {0} must match {1}.'.format(
                            invite, user.username
                        )
                    }, status=status.HTTP_400_BAD_REQUEST)

                token, _ = Token.objects.get_or_create(user = user)
                note = Notification()
                note.throttled_email(template='account_create',
                    username = user.username,
                    magic_link =  settings.CLIENT_HOST + '/forgot_password/' + encrypt(token))
                return Response({
                    'status': 'Invitation link sent to {0}.'.format(user.email, ),
                }, status=status.HTTP_200_OK)

        return Response(serializer.errors,
                        status=status.HTTP_401_UNAUTHORIZED)


class WhoAmIViewSet(viewsets.ReadOnlyModelViewSet):
    """
    provides the user information and profile of the currently logged in user
    GET Only.
    """
    queryset = User.objects.all()
    serializer_class = WhoAmISerializer
    # permission_classes = (permissions.IsAuthenticatedOrReadOnly,)


    @action(detail=False, methods=['get'], serializer_class=WhoAmISerializer,
        permission_classes=[permissions.IsAuthenticated],)
    def email(self, request):
        queryset = self.get_queryset()
        self.context={'request':request}
        serializer = WhoAmISerializer(queryset, many=False, context=self.context)
        test_email(self.request.user.username)
        return Response(serializer.data)


    def get_queryset(self):
        return User.objects.filter(username=self.request.user)
