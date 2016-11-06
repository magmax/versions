"""versionmgr URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.9/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url, include
from django.contrib import admin
from rest_framework.schemas import get_schema_view
from rest_framework.routers import DefaultRouter
from rest_framework_swagger.views import get_swagger_view

from version import views

router = DefaultRouter()
router.register(r'cluster', views.ClusterViewSet)
router.register(r'host', views.HostViewSet)
router.register(r'deployment', views.DeploymentViewSet)
router.register(r'application', views.ApplicationViewSet)
router.register(r'version', views.VersionViewSet)
router.register(r'component', views.ComponentViewSet)
router.register(r'service', views.ServiceViewSet)

urlpatterns = [
    url(r'^api/', include(router.urls)),
    url(r'^version/$', views.version_write),
    url(r'^$', views.index, name="home"),
    url(r'^main.js$', views.javascript, name="javascript"),
    url(r'^accounts/', include('django.contrib.auth.urls')),
    url(r'^register/?$', views.registerView, name='register'),
    url(r'^register/confirm/(?P<key>.+)/?$', views.registerConfirmView, name='registration_confirm'),
    url(r'^admin/', admin.site.urls),
    url(r'^api-auth/', include('rest_framework.urls', namespace='rest_framework')),
]

# Swagger UI
swagger_schema_view = get_swagger_view(title='Pastebin API')
urlpatterns += [
    url(r'^swagger/$',
        swagger_schema_view),
]
