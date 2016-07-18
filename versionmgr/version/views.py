import json
from collections import defaultdict
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET

from . import models


@require_POST
def version(request):
    data = json.loads(request.body.decode("utf-8"))
    host, _ = models.Host.objects.get_or_create(
        name=data.get('host') or request.META['REMOTE_HOST']
    )
    app, _ = models.Application.objects.get_or_create(
        name=data['application']
    )
    version, _ = models.Version.objects.get_or_create(
        uri=data['uri'],
    )

    prev_host = version.host.name if version.host else ""
    prev_app = version.application.name if version.application else ""
    prev_version = version.name

    version.host = host
    version.application = app
    version.name = data['version']

    if prev_host != host.name or prev_app != app.name or prev_version != version.name:
        version.save()

    return JsonResponse(dict(result='ok', previous=dict(host=prev_host, application=prev_app, version=prev_version)))


@require_GET
def show_by_host(request):
    data = dict(versions={}, hosts=set(), applications=set())
    for version in models.Version.objects.all():
        host = version.host.name
        app = version.application.name
        data['hosts'].add(host)
        data['applications'].add(app)
        if host not in data['versions']:
            data['versions'][host] = {}
        data['versions'][host][app] = dict (
            name=version.name,
        )



    return render(request, 'by_host.html', data)
