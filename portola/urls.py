from django.urls import path, include
from rest_framework.routers import DefaultRouter
from portola import views, tendemail
from rest_framework.authtoken import views as rest_framework_views
from rest_framework.schemas import get_schema_view
# from django.contrib import admin
from django.urls import path
from django.conf import settings
from django.conf.urls import url
from rest_framework import serializers

schema_view = get_schema_view(title='Pastebin API')

# Create a router and register our viewsets with it.
router = DefaultRouter()
router.register(r'whoami',views.WhoAmIViewSet, base_name='whoami')
router.register(r'bootstrap', views.BootstrapViewSet, base_name='bootstrap')
router.register(r'companies', views.CompanyViewSet)
router.register(r'documents', views.DocumentViewSet)
router.register(r'entities', views.EntityViewSet)
router.register(r'faq', views.FaqViewSet)
router.register(r'newsfeed', views.NewsFeedViewSet)
router.register(r'profiles', views.ProfileViewSet)
router.register(r'projects', views.ProjectViewSet)
router.register(r'pvmodel', views.PVModelViewSet)
router.register(r'users', views.UserViewSet)
router.register(r'tags', views.TagViewSet)
router.register(r'log', views.ApiRequestLogViewSet)
router.register(r'requests',views.RequestViewSet)
router.register(r'notifications',views.NotificationViewSet)


# The API URLs are now determined automatically by the router.
urlpatterns = [
    # path('admin/', admin.site.urls),
    path('api/forgot_password/', views.forgot_password),
    path('api/signin/', views.signin), #disabled unitl I can fix the request context
    # path('api/signin/',rest_framework_views.obtain_auth_token), # KLUGE to get moving
    # path('api/signin', views.user_info), # probably not needed
    path('api/tendemail/', tendemail.tendemail),
    path('api/', include(router.urls)),
    # Need this one for web login to api
    path('api-auth/', include('rest_framework.urls')),
]#+ static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# if settings.DEBUG:
#     urlpatterns += url(
#         r'^$', 'django.contrib.staticfiles.views.serve', kwargs={
#             'path': 'index.html', 'document_root': settings.STATIC_ROOT}),

# This is from: https://chrisbartos.com/articles/how-to-implement-token-authentication-with-django-rest-framework/
# for token auth.

# from django.conf.urls import url
# from django.conf import settings
# from django.conf.urls.static import static
#
# from . import views as local_view
# from rest_framework.authtoken import views as rest_framework_views
#
# urlpatterns = [
#     # Session Login
#     url(r'^login/$', local_views.get_auth_token, name='login'),
#     url(r'^logout/$', local_views.logout_user, name='logout'),
#     url(r'^auth/$', local_views.login_form, name='login_form'),
#     url(r'^get_auth_token/$', rest_framework_views.obtain_auth_token, name='get_auth_token'),
# ] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
