import json
import logging
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_GET
from django.shortcuts import render

from . import models

logger = logging.getLogger(__name__)


class UnserializationException(Exception):
    def __init__(self, got, expected):
        super().__init__('Expected %s, but got %s' % (expected, got))


class ObjectView(object):
    name_view_map = {}  # map with {property-name: view-class-name} format
    foreign_keys = {}

    def __init__(self):
        super()
        for k in self.foreign_keys:
            setattr(self, k, None)
        for k, v in self.name_view_map.items():
            setattr(self, k, [])

    @classmethod
    def from_model(cls, model):
        result = cls()
        for k in cls.fields:
            setattr(result, k, getattr(model, k))
        for name, viewclass in cls.foreign_keys.items():
            depmodel = getattr(model, name)
            setattr(result, name, viewclass.from_model(depmodel))
        for name, viewclass in cls.name_view_map.items():
            for depmodel in getattr(model, name).all():
                view = viewclass.from_model(depmodel)
                getattr(result, name).append(view)
        return result

    @classmethod
    def from_json(cls, _json):
        return cls.from_dict(json.loads(_json))

    @classmethod
    def from_dict(cls, _dict):
        if _dict.get('type') != str(cls):
            raise UnserializationException(cls, _dict.get('type'))
        result = cls()
        for k in cls.fields:
            setattr(result, k, _dict.get(k))
        for name, viewclass in cls.name_view_map.items():
            for x in _dict.get(name, []):
                getattr(result, name).append(viewclass.from_dict(x))
        return result

    def to_dict(self):
        result = dict(type=str(self.__class__))
        for k in self.fields:
            result[k] = getattr(self, k, None)
        for name in self.name_view_map:
            result[name] = [x.to_dict() for x in getattr(self, name)]
        return result

    def to_json(self):
        return json.dumps(self.to_dict())


class ClusterView(ObjectView):
    fields = ('id', 'name')


class HostView(ObjectView):
    fields = ('id', 'name', 'label')


class DeploymentView(ObjectView):
    fields = ('id', 'name', 'label')


class ApplicationView(ObjectView):
    fields = ('id', 'name', 'label', 'description')


class VersionView(ObjectView):
    fields = ('id', 'name')


class ServiceView(ObjectView):
    fields = ('id', )


class ClusterWithHostsView(ClusterView):
    name_view_map = dict(
        hosts=HostView,
    )


class ServiceWithDepsView(ServiceView):
    foreign_keys = dict(
        host=HostView,
        deployment=DeploymentView,
        application=ApplicationView,
        version=VersionView,
    )


class VersionDetail(VersionView):
    name_view_map = dict(
        services=ServiceWithDepsView,
    )


class DeploymentDetail(DeploymentView):
    name_view_map = dict(
        services=ServiceWithDepsView,
    )


class ApplicationDetail(ApplicationView):
    name_view_map = dict(
        services=ServiceWithDepsView,
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

            key = "{dep}|{app}|{host}".format(
                host=service.host.id,
                dep=service.deployment.id,
                app=service.application.id,
            )
            services[key] = dict(
                id=service.id,
                version=dict(
                    id=service.version.id,
                    name=service.version.name
                )
            )
    # sets to lists
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
    # out of any cluster
    standalone = [
        HostView.from_model(x).to_dict()
        for x in models.Host.objects.filter(cluster__isnull=True)
    ]

    if mode == 'json':
        return JsonResponse(dict(clusters=clusters, standalone=standalone))
    return render(request, 'clusters.html',
                  dict(clusters=clusters, standalone=standalone))


@require_GET
def host(request, pk, mode="json"):
    h = models.Host.objects.get(pk=pk)
    services = h.services.all()
    deployments = {}
    for service in services:
        deployment = service.deployment
        if deployment.id not in deployments:
            deployments[deployment.id] = dict(name=deployment.name, apps=[])
        application = ApplicationView()
        application.id = service.application.id
        application.name = service.application.name

        version = VersionView()
        version.id = service.version.id
        version.name = service.version.name

        deployments[deployment.id]['apps'].append(
            dict(
                name=deployment.name,
                application=application,
                version=version,
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
def host_list(request, mode="json"):
    hosts = [
        HostView.from_model(h)
        for h in models.Host.objects.order_by('name')
    ]

    if mode == 'json':
        return JsonResponse(dict(hosts=[h.to_dict() for h in hosts]))
    return render(request, 'hosts.html', dict(hosts=hosts))


@require_GET
def application(request, pk, mode="json"):
    a = models.Application.objects.get(pk=pk)
    data = ApplicationDetail.from_model(a)
    if mode == 'json':
        return JsonResponse(dict(app=data))
    return render(request, 'application.html', dict(app=data))


@require_GET
def deployment(request, pk, mode="json"):
    d = models.Deployment.objects.get(pk=pk)
    data = DeploymentDetail.from_model(d)

    if mode == 'json':
        return JsonResponse(dict(deployment=data))
    return render(request, 'deployment.html', dict(dep=data))


@require_GET
def version(request, pk, mode="json"):
    v = models.Version.objects.get(pk=pk)
    version = VersionDetail.from_model(v)
    if mode == 'json':
        return JsonResponse(dict(version=version))
    return render(request, 'version.html', dict(version=version))
