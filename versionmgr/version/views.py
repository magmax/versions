import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import render
from django.db.models import Model

from . import models

logger = logging.getLogger(__name__)


class UnserializationException(Exception):
    def __init__(self, got, expected):
        super().__init__('Expected %s, but got %s' % (expected, got))


class ObjectView(object):
    TYPE = 'ObjectView'
    _name_view_map = {}  # map with {property-name: view-class-name} format

    def __init__(self):
        super()
        for k, v in self._name_view_map.items():
            setattr(self, k, [])

    @classmethod
    def from_model(cls, model):
        result = cls()
        for k in cls._attribute_list():
            setattr(result, k, getattr(model, k))
        for name, viewclass in cls._name_view_map.items():
            for model in getattr(model, name).all():
                view = viewclass.from_model(model)
                getattr(result, name).append(view)
        return result

    @classmethod
    def from_json(cls, _json):
        return cls.from_dict(json.loads(_json))

    @classmethod
    def from_dict(cls, _dict):
        if _dict.get('type') != cls.TYPE:
            raise UnserializationException(cls.TYPE, _dict.get('type'))
        result = cls()
        for k in cls._attribute_list():
            setattr(result, k, _dict.get(k))
        for name, viewclass in cls._name_view_map.items():
            for x in _dict.get(name, []):
                getattr(result, name).append(viewclass.from_dict(x))
        return result


    def to_dict(self):
        result = dict(type=self.TYPE)
        for k, v in self._attribute_dict():
            result[k] = v
        for name in self._name_view_map:
            result[name] = [x.to_dict() for x in getattr(self, name)]
        return result

    def to_json(self):
        return json.dumps(self.to_dict())

    @classmethod
    def _attribute_list(cls):
        for k, v in cls.__dict__.items():
            if not cls._must_ignore(k, v):
                yield k

    def _attribute_dict(self):
        for k, v in self.__dict__.items():
            if not self._must_ignore(k, v):
                yield k, v

    @staticmethod
    def _must_ignore(k, v):
        return (
            k.startswith(('__', 'TYPE'))
            or callable(v)
            or isinstance(
                v,
                (
                    staticmethod,
                    classmethod,
                    Model,
                    list,
                    dict,
                )
            )
        )


class ClusterView(ObjectView):
    TYPE = 'Cluster'
    id = None
    name = None



class HostView(ObjectView):
    TYPE = 'Host'
    id = None
    name = None
    label = None


class DeploymentView(ObjectView):
    TYPE = 'Deployment'
    id = None
    name = None
    label = None


class ApplicationView(ObjectView):
    TYPE = 'Application'
    id = None
    name = None
    label = None
    description = None


class VersionView(ObjectView):
    TYPE = 'Version'
    id = None
    name = None


class ServiceView(ObjectView):
    TYPE = "Service"
    id = None


class ClusterWithHostsView(ObjectView):
    TYPE = "ClusterWithHosts"
    id = None
    name = None
    _name_view_map = dict(
        hosts=HostView,
    )


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

    service, created = models.Service.objects.get_or_create(
        host=host,
        application=app,
        deployment=deployment,
        defaults=dict(
            version=version
        )
    )
    prev_version = None if created else service.version.name
    service.version = version
    service.save()

    return JsonResponse(dict(result='ok', previous=dict(version=prev_version)))


@require_GET
def cluster(request, pk, mode="json"):
    c = models.Cluster.objects.get(pk=pk)
    apps = {}
    deployments = {}
    applications = {}
    deployapps = {}
    services = {}
    hosts = {}
    for host in c.hosts.all():
        hosts[host.id] = host.name
        for service in host.services.all():
            deployments[service.deployment.id] = service.deployment.name
            applications[service.application.id] = service.application.name
            if service.deployment.id not in deployapps:
                deployapps[service.deployment.id] = set()
            deployapps[service.deployment.id].add(service.application.id)

            key = "{dep}|{app}|{host}".format(host=service.host.id, dep=service.deployment.id, app=service.application.id)
            services[key] = dict(
                id=service.id,
                version=dict(
                    id=service.version.id,
                    name=service.version.name
                )
            )
    #sets to lists
    for k, v in deployapps.items():
        deployapps[k] = list(v)

    data = dict(
        id=c.id,
        name=c.name,
        attributes=dict(
            (x.name, x.value) for x in c.attributes.all()
        ),
        hosts=hosts,
        deployments=deployments,
        applications=applications,
        services=services,
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
            ClusterWithHostsView.from_model(cluster).to_dict()
        )
    #out of any cluster
    standalone = [HostView.from_model(x).to_dict() for x in models.Host.objects.filter(cluster__isnull=True)]

    if mode == 'json':
        return JsonResponse(dict(clusters=clusters, standalone=standalone))
    return render(request, 'clusters.html', dict(clusters=clusters, standalone=standalone))


@require_GET
def host(request, pk, mode="json"):
    h = models.Host.objects.get(pk=pk)
    services = h.services.all()
    deployments = {}
    for service in services:
        deployment = service.deployment
        if deployment.id not in deployments:
            deployments[deployment.id] = dict(name=deployment.name, apps=[])
        deployments[deployment.id]['apps'].append(
            dict(
                name=deployment.name,
                application=dict(
                    id=service.application.id,
                    name=service.application.name,
                ),
                version=dict(
                    id=service.version.id,
                    name=service.version.name,
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
    services = a.services.all()
    data = dict(
        id=a.id,
        name=a.label or a.name,
        description=a.description,
        services=[
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
            for x in services
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
    services = d.services.all()
    data = dict(
        id=d.id,
        name=d.label or d.name,
        services=[
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
            for x in services
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
    services = {}
    for service in v.services.all():
        services[service.id] = dict(
            host=dict(
                id=service.host.id,
                name=service.host.name,
            ),
            deployment=dict(
                id=service.deployment.id,
                name=service.deployment.name,
            ),
            application=dict(
                id=service.application.id,
                name=service.application.name,
            )
        )
    data = dict(
        id=v.id,
        name=v.name,
        services=services,
    )
    if mode == 'json':
        return JsonResponse(dict(version=data))
    return render(request, 'version.html', dict(version=data))
