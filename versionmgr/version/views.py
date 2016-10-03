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


class AttributeView(ObjectView):
    fields = ('id', 'name', 'value')


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


class CustomerView(ObjectView):
    fields = ('id', 'name')


class ReleaseView(ObjectView):
    fields = ('id', 'name')


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


class ClusterDetail(VersionView):
    name_view_map = dict(
        attributes=AttributeView,
        hosts=HostView,
    )


class HostDetail(HostView):
    foreign_keys = dict(
        cluster = ClusterView,
    )
    name_view_map = dict(
        attributes=AttributeView,
    )

class VersionDetail(VersionView):
    name_view_map = dict(
        attributes=AttributeView,
        services=ServiceWithDepsView,
    )


class DeploymentDetail(DeploymentView):
    name_view_map = dict(
        attributes=AttributeView,
        services=ServiceWithDepsView,
    )


class ApplicationDetail(ApplicationView):
    name_view_map = dict(
        attributes=AttributeView,
        services=ServiceWithDepsView,
    )


class CustomerDetail(CustomerView):
    name_view_map = dict(
        attributes=AttributeView,
        deployments=DeploymentView,
    )


class ReleaseDetail(ReleaseView):
    name_view_map = dict(
        attributes=AttributeView,
        services=ServiceView,
    )


def generic_list(view, model, order_by):
    return [
        view.from_model(x)
        for x in model.objects.order_by(*order_by)
    ]


def to_dict(obj):
    if isinstance(obj, ObjectView):
        return obj.to_dict()
    if isinstance(obj, list):
        return [to_dict(x) for x in obj]
    if isinstance(obj, dict):
        return dict((k, to_dict(v)) for k, v in obj.items())
    return obj


def to_json(obj):
    return json.dumps(obj, default=to_dict)


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

    print(prev_version)
    print(to_dict(dict(version=prev_version)))
    return JsonResponse(dict(result='ok',
                             previous=to_dict(dict(version=prev_version))))


@require_GET
def index(request, mode="json"):
    if mode == 'json':
        return JsonResponse()
    return render(request, 'base.html')


@require_GET
def cluster(request, pk, mode="json"):
    c = models.Cluster.objects.get(pk=pk)
    data = ClusterDetail.from_model(c)
    if mode == 'json':
        return JsonResponse(to_dict(dict(cluster=data)))
    return render(request, 'cluster.html', dict(cluster=data))


@require_GET
def cluster_list(request, mode="json"):
    clusters = []
    for cluster in models.Cluster.objects.all():
        clusters.append(
            ClusterWithHostsView.from_model(cluster)
        )
    # out of any cluster
    standalone = [
        HostView.from_model(x)
        for x in models.Host.objects.filter(cluster__isnull=True)
    ]

    if mode == 'json':
        return JsonResponse(to_dict(dict(clusters=clusters,
                                         standalone=standalone)))
    return render(request, 'clusters.html',
                  dict(clusters=clusters, standalone=standalone))


@require_GET
def host(request, pk, mode="json"):
    h = models.Host.objects.get(pk=pk)
    data = HostDetail.from_model(h)
    if mode == 'json':
        return JsonResponse(dict(host=data))
    return render(request, 'host.html', dict(host=data))


@require_GET
def host_list(request, mode="json"):
    hosts = generic_list(HostView, models.Host, ['name'])

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
def application_list(request, mode="json"):
    objs = generic_list(ApplicationView, models.Application, ['label', 'name'])

    if mode == 'json':
        return JsonResponse(dict(applications=[x.to_dict() for x in objs]))
    return render(request, 'applications.html', dict(applications=objs))


@require_GET
def deployment(request, pk, mode="json"):
    d = models.Deployment.objects.get(pk=pk)
    data = DeploymentDetail.from_model(d)

    if mode == 'json':
        return JsonResponse(dict(deployment=data))
    return render(request, 'deployment.html', dict(dep=data))


@require_GET
def deployment_list(request, mode="json"):
    objs = generic_list(DeploymentView, models.Deployment, ['label', 'name'])

    if mode == 'json':
        return JsonResponse(dict(applications=[x.to_dict() for x in objs]))
    return render(request, 'deployments.html', dict(deployments=objs))


@require_GET
def version(request, pk, mode="json"):
    v = models.Version.objects.get(pk=pk)
    version = VersionDetail.from_model(v)
    if mode == 'json':
        return JsonResponse(dict(version=version))
    return render(request, 'version.html', dict(version=version))


@require_GET
def version_list(request, mode="json"):
    objs = generic_list(VersionView, models.Version, ['name'])

    if mode == 'json':
        return JsonResponse(dict(versions=[x.to_dict() for x in objs]))
    return render(request, 'versions.html', dict(versions=objs))


@require_GET
def customer(request, pk, mode="json"):
    v = models.Customer.objects.get(pk=pk)
    customer = CustomerDetail.from_model(v)
    if mode == 'json':
        return JsonResponse(dict(customer=customer))
    return render(request, 'customer.html', dict(customer=customer))


@require_GET
def customer_list(request, mode="json"):
    objs = generic_list(CustomerView, models.Customer, ['name'])

    if mode == 'json':
        return JsonResponse(dict(customers=[x.to_dict() for x in objs]))
    return render(request, 'customers.html', dict(customers=objs))


@require_GET
def release(request, pk, mode="json"):
    v = models.Release.objects.get(pk=pk)
    release = ReleaseDetail.from_model(v)
    if mode == 'json':
        return JsonResponse(dict(release=release))
    return render(request, 'release.html', dict(release=release))


@require_GET
def release_list(request, mode="json"):
    objs = generic_list(ReleaseView, models.Release, ['name'])

    if mode == 'json':
        return JsonResponse(dict(releases=[x.to_dict() for x in objs]))
    return render(request, 'releases.html', dict(releases=objs))
