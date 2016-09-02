import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import render

from . import models

logger = logging.getLogger(__name__)


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
        name=data['version']
    )
    deployment, _ = models.Deployment.objects.get_or_create(
        name=data.get('deployment', "default")
    )

    appinstance, created = models.AppInstance.objects.get_or_create(
        host=host,
        application=app,
        deployment=deployment,
        defaults=dict(
            version=version
        )
    )
    prev_version = None if created else appinstance.version.name
    appinstance.version = version
    appinstance.save()

    return JsonResponse(dict(result='ok', previous=dict(version=prev_version)))


class Item(object):
    def __init__(self, id, name):
        self.id = id
        self.name = name
        self.keys = []
        self.items = {}

    def __getitem__(self, key):
        return self.items[key.id]

    def __setitem__(self, key, value):
        self.keys.append(key.id)
        self.items[key.id] = Item(key, value)

    def __str__(self):
        return "<id: %s; name: %s; items: %s>" % (self.id, self.name, len(self.keys))


@require_GET
def cluster(request, pk, mode="json"):
    c = models.Cluster.objects.get(pk=pk)
    apps = {}
    deployments = {}
    applications = {}
    deployapps = {}
    instances = {}
    hosts = {}
    for host in c.hosts.all():
        hosts[host.id] = host.name
        for inst in host.app_instances.all():
            deployments[inst.deployment.id] = inst.deployment.name
            applications[inst.application.id] = inst.application.name
            if inst.deployment.id not in deployapps:
                deployapps[inst.deployment.id] = set()
            deployapps[inst.deployment.id].add(inst.application.id)

            key = "{dep}|{app}|{host}".format(host=inst.host.id, dep=inst.deployment.id, app=inst.application.id)
            instances[key] = dict(
                id=inst.id,
                version=dict(
                    id=inst.version.id,
                    name=inst.version.name
                )
            )

    data = dict(
        id=c.id,
        name=c.name,
        attributes={
            (x.name, x.value) for x in c.attributes.all()
        },
        hosts=hosts,
        deployments=deployments,
        applications=applications,
        instances=instances,
        deployapps=deployapps,
    )
    if mode == 'json':
        return JsonResponse(dict(cluster=data))
    return render(request, 'cluster.html', dict(cluster=data))


@require_GET
def cluster_list(request, mode="json"):
    clusters = []
    for cluster in models.Cluster.objects.all():
        clusters.append(
            dict(
                name=cluster.name,
                id=cluster.id,
                hosts={(x.id, x.name) for x in cluster.hosts.all()}
            )
        )
    #out of any cluster
    clusters.append(
        dict(
            hosts={(x.id, x.name) for x in models.Host.objects.filter(cluster__isnull=True)}
        )
    )
    if mode == 'json':
        return JsonResponse(dict(clusters=clusters))
    return render(request, 'clusters.html', dict(clusters=clusters))


@require_GET
def host(request, pk, mode="json"):
    h = models.Host.objects.get(pk=pk)
    appinstances = h.app_instances.all()
    deployments = {}
    for appinstance in appinstances:
        deployment = appinstance.deployment
        if deployment.id not in deployments:
            deployments[deployment.id] = dict(name=deployment.name, apps=[])
        deployments[deployment.id]['apps'].append(
            dict(
                name=deployment.name,
                application=dict(
                    id=appinstance.application.id,
                    name=appinstance.application.name,
                ),
                version=dict(
                    id=appinstance.version.id,
                    name=appinstance.version.name,
                )
            )
        )

    data = dict(
        id=h.id,
        name=h.name,
        label=h.label,
        attributes={
            (x.name, x.value) for x in h.attributes.all()
        },
        deployments=deployments,
    )
    if h.cluster:
        data['cluster'] = dict(
            id=h.cluster.id,
            name=h.cluster.name,
            attributes={
                (x.name, x.value) for x in h.cluster.attributes.all()
            },
        )

    if mode == 'json':
        return JsonResponse(dict(host=data))
    return render(request, 'host.html', dict(host=data))


@require_GET
def application(request, pk, mode="json"):
    a = models.Application.objects.get(pk=pk)
    instances = a.app_instances.all()
    data = dict(
        id=a.id,
        name=a.label or a.name,
        description=a.description,
        instances=[
            dict(
                host=dict(
                    id=x.host.id,
                    name=x.host.name,
                ),
                deployment=dict(
                    id=x.deployment.id,
                    name=x.deployment.name,
                ),
                version=dict(
                    id=x.version.id,
                    name=x.version.name,
                ),
            )
            for x in instances
        ],
        attributes={
            (x.name, x.value) for x in a.attributes.all()
        },
    )
    if mode == 'json':
        return JsonResponse(dict(app=data))
    return render(request, 'application.html', dict(app=data))

@require_GET
def deployment(request, pk, mode="json"):
    d = models.Deployment.objects.get(pk=pk)
    instances = d.app_instances.all()
    data = dict(
        id=d.id,
        name=d.label or d.name,
        instances=[
            dict(
                host=dict(
                    id=x.host.id,
                    name=x.host.name,
                ),
                application=dict(
                    id=x.application.id,
                    name=x.application.name,
                ),
                version=dict(
                    id=x.version.id,
                    name=x.version.name,
                ),
            )
            for x in instances
        ],
        attributes={
            (x.name, x.value) for x in d.attributes.all()
        },
    )
    if mode == 'json':
        return JsonResponse(dict(deployment=data))
    return render(request, 'deployment.html', dict(dep=data))


@require_GET
def version(request, pk, mode="json"):
    v = models.Version.objects.get(pk=pk)
    instances = {}
    for instance in v.app_instances.all():
        instances[instance.id] = dict(
            host=dict(
                id=instance.host.id,
                name=instance.host.name,
            ),
            deployment=dict(
                id=instance.deployment.id,
                name=instance.deployment.name,
            ),
            application=dict(
                id=instance.application.id,
                name=instance.application.name,
            )
        )
    data = dict(
        id=v.id,
        name=v.name,
        instances=instances,
    )
    if mode == 'json':
        return JsonResponse(dict(version=data))
    return render(request, 'version.html', dict(version=data))
