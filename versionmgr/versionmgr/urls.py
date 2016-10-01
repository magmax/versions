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
from django.conf.urls import url
from django.contrib import admin

from version import views


urlpatterns = [
    url(r'^version/$', views.version_write),
    url(r'^cluster/(?P<pk>\d+)/?$', views.cluster),
    url(r'^cluster/?$', views.cluster_list),
    url(r'^html/cluster/?$', views.cluster_list,
        dict(mode='html'), name="home"),
    url(r'^html/cluster/(?P<pk>\d+)/?$', views.cluster,
        dict(mode='html'), name="cluster"),
    url(r'^html/host/?$', views.host_list,
        dict(mode='html'), name="hosts"),
    url(r'^html/host/(?P<pk>\d+)/?$', views.host,
        dict(mode='html'), name="host"),
    url(r'^html/application/(?P<pk>\d+)/?$', views.application,
        dict(mode='html'), name="application"),
    url(r'^html/application/?$', views.application_list,
        dict(mode='html'), name="applications"),
    url(r'^html/deployment/(?P<pk>\d+)/?$', views.deployment,
        dict(mode='html'), name="deployment"),
    url(r'^html/deployment/?$', views.deployment_list,
        dict(mode='html'), name="deployments"),
    url(r'^html/version/(?P<pk>\d+)/?$', views.version,
        dict(mode='html'), name="version"),
    url(r'^html/version/?$', views.version_list,
        dict(mode='html'), name="versions"),
    url(r'^admin/', admin.site.urls),
]
