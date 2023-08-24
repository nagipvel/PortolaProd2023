from rest_framework import serializers
from .models import *
from .authentication import token_refresh
from rest_framework_tracking.models import APIRequestLog
from django.contrib.auth.models import User
from rest_framework.reverse import reverse_lazy
import datetime

class ApiRequestLogSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField()
    def get_username(self,obj): return obj.user.username
    # remote_addr = serializers.SerializerMethodField()
    #
    # def get_remote_addr(self, instance):
    #     print(self.remote_addr)

    class Meta:
        model = APIRequestLog
        # fields = '__all__'
        fields = (
            'id',
            'requested_at',
            'url',
            'user',
            'username',
            'path',
            'view',
            'response_ms',
            'view_method',
            'remote_addr',
            'host',
            'method',
             # 'query_params',
             # 'data',
             # 'response',
            'errors',
            'status_code',
        )
        # exclude=('data','query_params','response','remote_addr')

class ApiRequestLogDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = APIRequestLog
        fields = '__all__'
        # exclude=('data','query_params','response',)

class CompanySerializer(serializers.HyperlinkedModelSerializer):

    class Meta:
        model = Company
        fields =( 'name','url','website','country','bio',)

class DocumentListSerializer(serializers.HyperlinkedModelSerializer):
    # owner = serializers.ReadOnlyField(source='owner.username')
    name = serializers.SerializerMethodField()
    type_text = serializers.ReadOnlyField(source='get_type_display')
    disclosure_text = serializers.ReadOnlyField(source='get_disclosure_display')
    technology_tags = serializers.SlugRelatedField(
        many=True,
        slug_field='title',
        queryset=TechnologyTag.objects.all()
    )

    def get_name(self, obj):
        return obj.file.name

    def to_representation(self, instance):
        """Convert `file locstion` to download URL."""
        ret = super().to_representation(instance)
        ret['file'] = ret['url'] + 'download/'
        return ret

    class Meta:
        model = Document
        fields = (
            'id',
            'url',
            'file',
            'name',
            'title',
            'project',
            'bom',
            'issued_date',
            'factory_witness_date',
            'technology_tags',
            # 'permitted_entities',
            'product_type',
            'type',
            'type_text',
            # 'box_id',
            'disclosure',
            'disclosure_text',
            )

class DocRequestSerializer(serializers.ModelSerializer):
    """
    This serializer is for the creation of document requets
    """
    class Meta:
        model = Request
        fields = ('id','url','requestor','created',
            'resolved','expires','status','document','requestor_comment',
            'approver_comment')

    def create(self, validated_data):
        # should do duplicate check here
        doc_request = Request.objects.create(**validated_data)
        return doc_request

class DocumentDisclosureSerializer(serializers.ModelSerializer):
    """
    This serializer is specifically for updating disclosure
    """
    class Meta:
        model = Document
        fields = ('id','disclosure','disclosure_date')

    def update(self, instance, validated_data):
        # document_data = validated_data.pop('disclosure')
        instance.disclosure = validated_data.get('disclosure')
        instance.disclosure_date = validated_data.get('disclosure_date')
        instance.save()

        return instance

class DocumentNameSerializer(serializers.ModelSerializer):
    """
    This serializer is specifically for returning name and ID
    document metadata
    """
    name = serializers.SerializerMethodField()
    type_text = serializers.ReadOnlyField(source='get_type_display')
    disclosure_text = serializers.ReadOnlyField(source='get_disclosure_display')
    project_number = serializers.ReadOnlyField(source = 'project.number')
    entity_display_name = serializers.ReadOnlyField(source = 'entity.display_name')
    technology_tags = serializers.SlugRelatedField(
        many=True,
        slug_field='title',
        queryset=TechnologyTag.objects.all()
    )

    def get_project_number(self, object):
        pass

    def get_name(self, obj):
        return obj.file.name

    def to_representation(self, instance):
        """Convert `file location` to download URL."""
        ret = super().to_representation(instance)
        ret['file'] = ret['url'] + 'download/'
        return ret

    class Meta:
        model = Document
        fields = ('id','url',
        'file',
        'name',
        'entity_display_name',
        'title',
        'issued_date',
        'project_number',
        'bom',
        # 'project_info',
        'technology_tags',
        # 'permitted_entities',
        'product_type',
        'type',
        'type_text',
        # 'box_id',
        # 'requests',
        'disclosure','disclosure_text',)

class DocumentDashboardSerializer(serializers.HyperlinkedModelSerializer):
    entity_display_name = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    def get_following(self,obj):
        user = self.context.get('request').user
        if user:
            for follower in obj.entity.followers.all():
                if user.profile.entity == follower.profile.entity:
                    return True
            for follower in obj.project.followers.all():
                if user.profile.entity == follower.profile.entity:
                    return True
        return False

    def get_entity_display_name(self,obj):
        return obj.entity.display_name
    def get_name(self, obj):
        return obj.file.name
    def to_representation(self, instance):
        """Convert `file location` to download URL."""
        ret = super().to_representation(instance)
        ret['file'] = ret['url'] + 'download/'
        return ret

    class Meta:
        model = Document
        fields = (
            'id',
            'following',
            'entity_display_name',
            'issued_date',
            'name',
            'title',
            'file',
            'url',
            'disclosure',
        )

class DocumentSerializer(serializers.HyperlinkedModelSerializer):
    # owner = serializers.ReadOnlyField(source='owner.username')
    # factory_witness_date = serializers.SerializerMethodField()
    factory_witness_date = serializers.DateField(required=False)
    project_info = serializers.SerializerMethodField()
    project_number = serializers.SerializerMethodField()
    project_type_text = serializers.SerializerMethodField()
    entity_display_name = serializers.SerializerMethodField()
    type_text = serializers.ReadOnlyField(source='get_type_display')
    disclosure_text = serializers.ReadOnlyField(source='get_disclosure_display')
    technology_tags = serializers.SlugRelatedField(
        many=True,
        slug_field='title',
        queryset=TechnologyTag.objects.all()
    )
    requests = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()
    disclosure = serializers.SerializerMethodField()

    # TODO: This isn't perfect yet, but I like it better
    # def create(self, validated_data):
    #     print(validated_data['file'].name)
    #     validated_data['name'] = validated_data['file'].name
    #     print(validated_data.get('disclosure','PENDING'))
    #     validated_data['disclosure'] = validated_data.get('disclosure','PENDING')
    #     super().create(**validated_data)

    def validate(self, instance):
        entity = instance['entity']
        project = instance['project']
        if entity != project.customer:
            raise serializers.ValidationError("entity must be equal to project.entity")
        return instance

    def to_representation(self, instance):
        """Convert `file location` to download URL."""
        ret = super().to_representation(instance)
        ret['file'] = ret['url'] + 'download/'
        return ret

    # this is to add requests made by the current user against a document
    # will populate if there is a request by the same entity
    def get_requests(self, object):
        # requests_qs = object.requests.all()
        filtered_qs =[]
        user = self.context.get('request').user
        filtered_qs.append(object.requests.filter(requestor__profile__entity=user.profile.entity).first())
        serializer = RequestSerializer(filtered_qs, many=True, context=self.context)
        return serializer.data

    def get_entity_display_name(self, obj):
        return obj.entity.display_name

    # This is very wrong:
    def get_disclosure(self,obj):
        # print('IN DISCLOSURE')
        if self.context.get('request').user.is_superuser:
            return obj.disclosure
        if obj.disclosure == 'PENDING':
            if self.context.get('request').user != obj.project.document_approver:
                return None
        return obj.disclosure

    def get_name(self, obj):
        return obj.file.name

    def get_project_info(self, object):
        project_object = object.project
        qs=[]
        qs.append(project_object)
        serializer = ProjectNameSerializer(qs, many=True, context=self.context)
        return serializer.data

    def get_project_number(self, object):
        return object.project.number

    def get_project_type_text(self, object):
        return object.project.get_type_display()

    class Meta:
        model = Document
        fields = ('id','url','file',
        # 'owner',
        'name',
        'title',
        'entity',
        'entity_display_name',
        'issued_date',
        'factory_witness_date',
        'bom',
        'project',
        'project_number',
        'project_type_text',
        'project_info',
        'technology_tags',
        'permitted_entities',
        'product_type',
        'type',
        'type_text',
        'box_id',
        'requests',
        'disclosure','disclosure_text','disclosure_date',
        )
        read_only_fields = ['disclosure_date','box_id',]

class EntitySubSerializer(serializers.PrimaryKeyRelatedField):
    type_text = serializers.ReadOnlyField(source='get_type_display')
    company_type_text = serializers.ReadOnlyField(source='get_company_type_display')


    class Meta:
        model = Entity
        fields = ('id','url',
        'company',
        'legal_name',
        'following',
        'type',
        'type_text',
        'company_type_text',
        'website',
        'country')

class EntityFollowSerializer(serializers.HyperlinkedModelSerializer):
    # Create a custom method field
    current_user = serializers.SerializerMethodField('_user')

    # Use this method for the custom field
    def _user(self, obj):
        request = getattr(self.context, 'request', None)
        if request:
            return request.user

    class Meta:
        model = Entity
        fields = ('id','followers', 'current_user')

    def update(self, instance, validated_data):
        entity_data = validated_data.pop('entity')
        instance.followers.append(validated_data.get('current_user'))
        instance.save()

        return instance

class EntityNameSerializer(serializers.ModelSerializer):
    company_type_text = serializers.ReadOnlyField(source='get_company_type_display')
    class Meta:
        model = Entity
        fields = ('display_name','company_type_text')

class EntitySerializer(serializers.HyperlinkedModelSerializer):
    # users = serializers.HyperlinkedRelatedField(many=True, view_name='users-detail', read_only=True)
    type_text = serializers.ReadOnlyField(source='get_type_display')
    followers = serializers.SerializerMethodField()
    company_type_text = serializers.ReadOnlyField(source='get_company_type_display')
    following = serializers.SerializerMethodField()
    project_count = serializers.SerializerMethodField()
    document_count = serializers.SerializerMethodField()
    followers_count = serializers.SerializerMethodField()
    followers_new = serializers.SerializerMethodField()

    # This is if we decide full entity gets all follows
    def entity_following(self, obj):
        user = self.context.get('request').user
        if user:
            for follower in obj.followers.all():
                if user.profile.entity == follower.profile.entity:
                    return True
        return False

    def get_document_count(self, obj):
        return (obj.document_set.count())

    # current implementation: User only controls own following
    def get_following(self, obj):
        return (self.context.get('request').user in obj.followers.all())

    def get_followers(self, object):
        followers_qs = object.followers.all()
        qs=[]
        for follower in followers_qs:
            if follower.profile.entity not in qs:
                qs.append(follower.profile.entity)
        serializer = EntityNameSerializer(qs, many=True, context=self.context)
        return serializer.data

    def get_followers_new(self, obj):
        count = obj.followers.count()
        # this math is VERY wrong...
        for project in obj.project_set.all():
            count = count + project.followers.count()
        return count

    def get_followers_count(self, obj):
        count = obj.followers.count()
        # this math is wrong...
        for project in obj.project_set.all():
            count = count + project.followers.count()
        return count

    def get_project_count(self, obj):
        return (obj.project_set.count())


    class Meta:
        model = Entity
        fields = ('id','url',
        'company',
        'legal_name',
        'display_name',
        'public',
        'project_count',
        'document_count',
        'followers_count',
        'followers_new',
        'following',
        'type',
        'company_type',
        'followers',
        'type_text',
        'company_type_text',
        'website','country')

class EntityListSerializer(serializers.HyperlinkedModelSerializer):
    following = serializers.SerializerMethodField()

    # current implementation: User only controls own following
    def get_following(self, obj):
        return (self.context.get('request').user in obj.followers.all())

    class Meta:
        model = Entity
        fields = ('id','url',
        'company',
        'type',
        'company_type',
        'legal_name',
        'display_name',
        'public',
        'following',
        'website','country')

class FaqSerializer(serializers.HyperlinkedModelSerializer):
    type_text = serializers.ReadOnlyField(source='get_type_display')

    class Meta:
        # list_serializer_class = FilteredFaqSerializer
        model = Faq
        fields = ('id','url','created_by','last_updated_by',
            'last_updated','section','type','type_text','subject','body')


class NewsFeedSerializer(serializers.HyperlinkedModelSerializer):
    # users = serializers.HyperlinkedRelatedField(many=True, view_name='users-detail', read_only=True)
    type_text = serializers.ReadOnlyField(source='get_type_display')

    class Meta:
        # list_serializer_class = FilteredFaqSerializer
        model = NewsFeed
        fields = ('id','url','created_by','last_updated_by','last_updated',
            'type','type_text','subject','body')

class NotificationQueueSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = NotificationQueue
        fields = '__all__'

class LostPasswordSerializer(serializers.Serializer):
    """
    Serializer for lost password endpoint.
    """
    new_password = serializers.CharField(required=True)

class PasswordSerializer(serializers.Serializer):
    """
    Serializer for password change endpoint.
    """
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True)

class ProfileDetailSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    # This is correct for the whoami call
    entity = EntitySerializer(many=False)

    class Meta:
        model = Profile
        fields = ('user','id','url','bio','location','birth_date',
            'entity',
            # 'current_user'
            )
    # Use this method for the custom field
    def _user(self, obj):
        request = getattr(self.context, 'request', None)
        if request:
            return request.user

class ProfileSerializer(serializers.HyperlinkedModelSerializer):
    user = serializers.ReadOnlyField(source='user.username')
    entity_legal_name = serializers.ReadOnlyField(source='entity.legal_name')
    # This is correct for the whoami call
    # entity = EntitySerializer(many=False)

    # This is the one we want on the form for POST... Can wait
    entity = EntitySubSerializer(many=False, queryset=Entity.objects.all() )
    # current_user = serializers.SerializerMethodField('_user')

    class Meta:
        model = Profile
        fields = ('user','id','url','bio','location','birth_date',
            'entity','entity_legal_name'
            # 'project_followers',
                # 'current_user'
            )
    # Use this method for the custom field
    def _user(self, obj):
        request = getattr(self.context, 'request', None)
        if request:
            return request.user

class ProjectFollowSerializer(serializers.HyperlinkedModelSerializer):
    # Create a custom method field
    current_user = serializers.SerializerMethodField('_user')

    # Use this method for the custom field
    def _user(self, obj):
        request = getattr(self.context, 'request', None)
        if request:
            return request.user

    class Meta:
        model = Project
        fields = ('id','followers', 'current_user')

    def update(self, instance, validated_data):
        project_data = validated_data.pop('project')
        instance.followers.append(validated_data.get('current_user'))
        instance.save()

        return instance


class ProjectNumberSerializer(serializers.ModelSerializer):

    class Meta:
        model = Project
        fields = (
            'number',
            )

class ProjectNameSerializer(serializers.ModelSerializer):
    type_text = serializers.ReadOnlyField(source='get_type_display')

    class Meta:
        model = Project
        fields = ('number','type_text')

class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    # customer = EntitySerializer(many=False,
    #     queryset=Entity.objects.all(),
    #     read_only=True)
    # customer = EntitySerializer(many=False)
    # customer = EntitySubSerializer(many=False, queryset=Entity.objects.all() )

    type_text = serializers.ReadOnlyField(source='get_type_display')
    # document_project = serializers.PrimaryKeyRelatedField(many=True, read_only=True)
    document_project = DocumentListSerializer(many=True, read_only=True)
    followers = serializers.SerializerMethodField()
    following = serializers.SerializerMethodField()
    customer_name = serializers.SerializerMethodField()
    primary_contact_user = serializers.SerializerMethodField()
    primary_contact_name = serializers.SerializerMethodField()
    document_approver_user = serializers.SerializerMethodField()
    document_approver_name = serializers.SerializerMethodField()
    pvel_manager_user = serializers.SerializerMethodField()
    pvel_manager_name = serializers.SerializerMethodField()
    last_document_date = serializers.SerializerMethodField()

    def get_customer_name(self, obj):
        return obj.customer.display_name
    def get_primary_contact_user(self, obj):
        return obj.primary_contact.username
    def get_primary_contact_name(self, obj):
        name = '{}, {}'.format(obj.primary_contact.last_name, obj.primary_contact.first_name)
        return name
    def get_document_approver_user(self, obj):
        return obj.document_approver.username
    def get_document_approver_name(self, obj):
        name = '{}, {}'.format(obj.document_approver.last_name, obj.document_approver.first_name)
        return name
    def get_pvel_manager_user(self, obj):
        return obj.pvel_manager.username
    def get_pvel_manager_name(self, obj):
        name = '{}, {}'.format(obj.pvel_manager.last_name, obj.pvel_manager.first_name)
        return name
    def get_last_document_date(self, obj):
        # TODO: Replace document_project with document_set
        try:
            last_date = obj.document_project.all().order_by('issued_date').last().issued_date
        except:
            last_date = None
        return last_date

    def get_followers(self, object):
        followers_qs = object.followers.all()
        qs=[]
        for follower in followers_qs:
            if follower.profile.entity not in qs:
                qs.append(follower.profile.entity)
        serializer = EntityNameSerializer(qs, many=True, context=self.context)
        return serializer.data

    # This is if we decide full entity gets all follows
    def entity_following(self, obj):
        user = self.context.get('request').user
        if user:
            for follower in obj.followers.all():
                if user.profile.entity == follower.profile.entity:
                    return True
        return False

    # current implementation: User only controls own following
    def get_following(self, obj):
        return (self.context.get('request').user in obj.followers.all())

    class Meta:
        model = Project
        fields = ('id','url','number','status',
            'salesforce_id',
            'name',
            'document_approver',
            'document_approver_user',
            'document_approver_name',
            'customer',
            'customer_name',
            'following',
            'type',
            'type_text',
            'contract_signature',
            'last_document_date',
            'primary_contact',
            'primary_contact_user',
            'primary_contact_name',
            'pvel_manager',
            'pvel_manager_user',
            'pvel_manager_name',
            'followers',
            'document_project',
            )

class PVModelSerializer(serializers.HyperlinkedModelSerializer):
    created_by = serializers.ReadOnlyField(source='created_by.username')

    class Meta:
        model = PVModel
        fields = '__all__'

class RequestBatchSerializer(serializers.ModelSerializer):

    class Meta:
        model = Request
        fields = ('id','status')

class RequestNewSerializer(serializers.HyperlinkedModelSerializer):
    issued_date = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    file = serializers.SerializerMethodField()
    name = serializers.SerializerMethodField()

    # KLUGE: There has to be a better way to get the download link
    def get_file(self, obj):
        request = self.context.get('request')
        url = reverse_lazy('api-root', request=request)
        docid = obj.document.id
        return str(url) + 'documents/' + str(docid) + '/download/'

    def get_name(self, obj):
        return obj.document.name

    def get_issued_date(self, obj):
        return obj.document.issued_date

    def get_title(self, obj):
        return obj.document.title

    class Meta:
        model = Request
        fields = (
        'name',
        'status',
        'issued_date',
        'title',
        'file',
        'id'
        )

class RequestSerializer(serializers.HyperlinkedModelSerializer):
    requestor_company = serializers.SerializerMethodField()
    document = serializers.SerializerMethodField()
    status = serializers.SerializerMethodField()
    # requestor = serializers.ReadOnlyField(source='get_requestor_display')

    def get_document(self, obj):
        serializer = DocumentNameSerializer(obj.document, many=False, context=self.context)
        return serializer.data

    def get_requestor_company(self, obj):
        requestor = obj.requestor
        qs=[]
        qs.append(requestor.profile.entity)
        serializer = EntityNameSerializer(qs, many=True, context=self.context)
        return serializer.data

    def get_status(self, obj):
        if obj.status == 'ACTIVE':
            if (self.context.get('request').user == obj.document.project.document_approver or
                self.context.get('request').user == obj.requestor):
                    pass
            else:
                return None
        return obj.status

    class Meta:
        model = Request
        fields = (
            'id',
            'url',
            # 'requestor',
            # 'requestor_name',
            'requestor_company','created',
            'resolved','expires','status','document','requestor_comment',
            'approver_comment')


class TagSerializer(serializers.ModelSerializer):
    type_text = serializers.ReadOnlyField(source='get_type_display')
    class Meta:
        model = TechnologyTag
        fields = ('id','url','title','type','type_text',
            # 'name',
            )

class UserSerializer(serializers.HyperlinkedModelSerializer):
    profile = ProfileSerializer(many=False)
    # admin = request.user.is_superuser # at some point may want to show admin
    # entities_following = serializers.HyperlinkedRelatedField(
    #     many=True,
    #     queryset=Entity.objects.all(),
    #     view_name='entity-detail'
    # )
    # projects_following = serializers.HyperlinkedRelatedField(
    #     many=True,
    #     queryset=Project.objects.all(),
    #     view_name='project-detail'
    # )
    class Meta:
        model = User
        fields = ('id', 'email',
                'is_active','is_staff', 'is_superuser', 'date_joined',
                # 'entities_following',
                # 'projects_following',
                'url','username',
                'first_name','last_name','profile',
                'password',
                )
        read_only_fields = (
            # 'username',
            'user',
            # 'entities_following',
            # 'projects_following',
            'auth_token', 'date_joined',
            )

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')
        user = User.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        profile_data['user'] = user
        Profile.objects.create(**profile_data)
        return user

    def update(self, instance, validated_data):
        from django.contrib.auth.hashers import is_password_usable
        profile_data = validated_data.pop('profile',None)
        # Update UserProfile data
        try:
            if not instance.profile:
                pass
        except:
            Profile.objects.create(user=instance, **profile_data)

        if profile_data:
            # Update Profile data
            ins = instance.profile
            ins.bio = profile_data.get('bio', instance.profile.bio)
            ins.location = profile_data.get('location', instance.profile.location)
            ins.birth_date = profile_data.get('birth_date', instance.profile.birth_date)
            # instance.profile.box_user = profile_data.get('uid', instance.profile.box_user)
            ins.save()

        # update user data by hand:
        if validated_data.get('password',instance.password) != instance.password:
            instance.set_password(validated_data.get('password'))

        if self.context.get('request').user.is_superuser:
            # Superuser API access:
            instance.email = validated_data.get('email',instance.email)
            instance.username = validated_data.get('username',instance.username)
            instance.is_active = validated_data.get('is_active',instance.is_active)
            instance.is_staff = validated_data.get('is_staff',instance.is_staff)
            instance.is_superuser = validated_data.get('is_superuser',instance.is_superuser)

        instance.first_name = validated_data.get('first_name',instance.first_name)
        instance.last_name = validated_data.get('last_name',instance.last_name)
        instance.save()

        return instance

class WhoAmISerializer(serializers.HyperlinkedModelSerializer):
    profile = ProfileDetailSerializer(many=False)
    token = serializers.SerializerMethodField()
    entities_following = serializers.HyperlinkedRelatedField(
        many=True,
        queryset=Entity.objects.all(),
        view_name='entity-detail'
    )
    projects_following = serializers.HyperlinkedRelatedField(
        many=True,
        queryset=Project.objects.all(),
        view_name='project-detail'
    )
    def get_token(self, object):
        token, _ = Token.objects.get_or_create(user = object)
        token = token_refresh(token)
        return token.key

    class Meta:
        model = User
        fields = ('id', 'email',
                'token',
                'is_active','is_staff', 'is_superuser', 'date_joined',
                'url','username',
                'entities_following',
                'projects_following',
                'first_name','last_name','profile')
        read_only_fields = (
            # 'username',
            'user',
            'token', 'date_joined',)

class ResendNotificationSerializer(serializers.Serializer):
    password = serializers.CharField(required = True)

class InviteUserSerializer(serializers.Serializer):
    username = serializers.CharField(required = True)

class ForgotPasswordSerializer(serializers.Serializer):
    username = serializers.CharField(required = True)

class UserSigninSerializer(serializers.Serializer):
    username = serializers.CharField(required = True)
    password = serializers.CharField(required = True)

class TokenSigninSerializer(serializers.Serializer):
    token = serializers.CharField(required = True)
