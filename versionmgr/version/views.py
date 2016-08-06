import json
import datetime
from collections import OrderedDict
from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.utils import timezone

from . import models


@require_POST
def version(request):
    data = json.loads(request.body.decode("utf-8"))
    host, host_created = models.Host.objects.get_or_create(
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

    #if prev_host != host.name or prev_app != app.name or prev_version != version.name:
    version.save()

    return JsonResponse(dict(result='ok', previous=dict(host=prev_host, application=prev_app, version=prev_version)))


@require_GET
def show_by_host(request):
    data = {}
    versions = OrderedDict()
    apps = set()
    time_limit = timezone.now() - datetime.timedelta(hours=6)
    data['time_limit'] = time_limit
    for version in models.Version.objects.order_by('host__name'):
        cluster = version.host.cluster.name if version.host.cluster else "<none>"
        host = version.host.name
        app = version.application.name
        apps.add(app)
        if cluster not in versions:
            versions[cluster] = OrderedDict()
        if host not in versions[cluster]:
            versions[cluster][host] = OrderedDict()
        versions[cluster][host][app] = dict (
            name=version.name,
            updated=version.updated,
            outdated=version.updated < time_limit,
        )
        data = dict(
            versions=versions,
            apps=sorted(apps),
        )
    return render(request, 'by_host.html', data)


@require_GET
def cluster(request, pk):
    c = models.Cluster.objects.get(pk=pk)
    return render(request, 'cluster.html', {'cluster':c})

@require_GET
def cluster_list(request):
    clusters = []
    for cluster in models.Cluster.objects.all():
        clusters.append(
            dict(
                name=cluster.name,
                id=cluster.id,
            )
        )
    return JsonResponse(dict(clusters=clusters))
