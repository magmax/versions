import json
from collections import OrderedDict
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET

from . import models


@require_POST
def version(request):
    data = json.loads(request.body.decode("utf-8"))
    if data.get('cluster'):
        cluster, cluster_created = models.Cluster.objects.get_or_create(
            name=data.get('cluster')
        )
    else:
        cluster, cluster_created = None, False
    host, host_created = models.Host.objects.get_or_create(
        name=data.get('host') or request.META['REMOTE_HOST']
    )
    if cluster or host_created or host.cluster is None or host.cluster.name != cluster.name:
        host.cluster = cluster
        host.save()
    app, _ = models.Application.objects.get_or_create(
        name=data['application']
    )
    version, _ = models.Version.objects.get_or_create(
        uri=data['uri'],
    )

    prev_cluster = version.host.cluster.name if version.host and version.host.cluster else ""
    prev_host = version.host.name if version.host else ""
    prev_app = version.application.name if version.application else ""
    prev_version = version.name

    version.host = host
    version.application = app
    version.name = data['version']

    if prev_host != host.name or prev_app != app.name or prev_version != version.name:
        version.save()

    return JsonResponse(dict(result='ok', previous=dict(host=prev_host, application=prev_app, version=prev_version, cluster=prev_cluster)))


@require_GET
def show_by_host(request):
    data = dict(versions=OrderedDict())
    for version in models.Version.objects.all():
        cluster = version.host.cluster.name if version.host.cluster else "<none>"
        host = version.host.name
        app = version.application.name
        if cluster not in data['versions']:
            data['versions'][cluster] = OrderedDict()
        if host not in data['versions'][cluster]:
            data['versions'][cluster][host] = OrderedDict()
        data['versions'][cluster][host][app] = dict (
            name=version.name,
        )

    return render(request, 'by_host.html', data)
