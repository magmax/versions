import re
import json
import logging
import hashlib
from functools import wraps
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import render, redirect
from django.contrib.auth.views import redirect_to_login, logout_then_login
from django.contrib import auth
from django.contrib.auth.decorators import permission_required
from django.contrib import messages
from django import db
from django.core.mail import send_mail
from django.conf import settings
from rest_framework import viewsets

from version import models, serializers, permissions

logger = logging.getLogger(__name__)


class ClusterViewSet(viewsets.ModelViewSet):
    queryset = models.Cluster.objects.all()
    serializer_class = serializers.ClusterWithDepsSerializer
    permission_classes = (permissions.IsRegistered, )


class HostViewSet(viewsets.ModelViewSet):
    queryset = models.Host.objects.all()
    serializer_class = serializers.HostWithDepsSerializer
    permission_classes = (permissions.IsRegistered, )


class DeploymentViewSet(viewsets.ModelViewSet):
    queryset = models.Deployment.objects.all()
    serializer_class = serializers.DeploymentWithDepsSerializer
    permission_classes = (permissions.IsRegistered, )


class ApplicationViewSet(viewsets.ModelViewSet):
    queryset = models.Application.objects.all()
    serializer_class = serializers.ApplicationWithDepsSerializer
    permission_classes = (permissions.IsRegistered, )


class VersionViewSet(viewsets.ModelViewSet):
    queryset = models.Version.objects.all()
    serializer_class = serializers.VersionWithDepsSerializer
    permission_classes = (permissions.IsRegistered, )


class ComponentViewSet(viewsets.ModelViewSet):
    queryset = models.Component.objects.all()
    serializer_class = serializers.ComponentWithDepsSerializer
    permission_classes = (permissions.IsRegistered, )


class ServiceViewSet(viewsets.ModelViewSet):
    queryset = models.Service.objects.all()
    serializer_class = serializers.ServiceWithDepsSerializer
    permission_classes = (permissions.IsRegistered, )


class UnserializationException(Exception):
    def __init__(self, got, expected):
        super().__init__('Expected %s, but got %s' % (expected, got))


@require_POST
def version_write(request):
    data = json.loads(request.body.decode("utf-8"))
    host, _ = models.Host.objects.get_or_create(
        name=data.get('host') or request.META['REMOTE_HOST']
    )
    app, _ = models.Application.objects.get_or_create(
        name=data['application']
    )
    version, _ = models.Version.objects.get_or_create(
        name=data['version']
    )
    deployment, _ = models.Deployment.objects.get_or_create(
        name=data.get('deployment', "default")
    )
    component, _ = models.Component.objects.get_or_create(
        version=version,
        application=app,
    )

    service, created = models.Service.objects.get_or_create(
        host=host,
        deployment=deployment,
        defaults=dict(
            component=component,
            arguments=data.get('arguments'),
        )

    )
    prev_version = None if created else service.component.version.name
    service.component = component
    service.save()

    return JsonResponse(dict(result='ok',
                             previous=to_dict(dict(version=prev_version))))

def registerView(request):
    if request.method == 'GET':
        return render(request, 'registration/register.html')
    email = request.POST.get('email')
    m = re.match("[\w_\-\+\.]+@([\w\-_]+\.[\w\-_\.]*\w)$", email)
    if not m:
        messages.error(request, 'The email %s does not look like an email'
                       % email)
        return redirect(registerView)
    if settings.COMPANY_DOMAIN and settings.COMPANY_DOMAIN != m.group(1):
        messages.error(request, 'The email %s does not belongs to the company'
                       % email)
    password = request.POST.get('password')
    try:
        user = auth.models.User.objects.create(
            username=email,
            email=email,
        )
        user.set_password(password)
        user.save()
    except db.utils.IntegrityError as e:
        messages.error(request, 'The user %s already exists.' % email)
        return redirect(registerView)
    except Exception as e:
        messages.error(request, 'The user %s could not be created. %s'
                       % (username, e))
        return redirect(registerView)

    url = "%s://%s" % (request.scheme, request.get_host())
    key = "%s.%s" % (user.id, hashlib.sha1(email.encode()).hexdigest()[:12])
    message = render(request, 'registration/email.html', {'key': key, 'site_url': url}).content.decode()
    send_mail(
        "Board registration",
        message,
        from_email=settings.EMAIL_FROM,
        recipient_list=[email],
        html_message=message,
    )
    messages.info("An email has been sent to you in order to confirm your email address")
    return redirect_to_login(request.get_full_path())


def registerConfirmView(request, key):
    id, mailhash = key.rsplit('.', 1)
    try:
        user = auth.models.User.objects.get(pk=id)
        if mailhash == hashlib.sha1(user.email.encode()).hexdigest()[:12]:
            user.groups.add(models.Group.get(settings.REGISTERED_GROUP))
            return redirect_to_login(request.get_full_path())
    except Exception as e:
        logger.exception("Semething bad happened confirming views")
    messages.error(request, "The confirmation url is not valid")
    return redirect(registerView)


@require_GET
def index(request):
    if not request.user.is_authenticated():
        return redirect_to_login(request.get_full_path())

    return render(request, 'logged.html')


@require_GET
def javascript(request):
    if not request.user.is_authenticated():
        return redirect_to_login(request.get_full_path())

    return render(request, 'javascript.js')
