from django.test import TestCase, RequestFactory
from django.test import Client
from django.contrib.auth.models import AnonymousUser, User

import json

from . import factories
from version import (
    views,
    models,
)


class InsertionByPublicAPITest(TestCase):
    def test_basic_insertion(self):
        c = Client()
        data = {'host': 'foo', 'application': 'bar', 'version': '1.2.3.4'}
        response = c.post(
            '/version/',
            json.dumps(data),
            content_type="application/json",
        )

        assert response.status_code == 200
        assert response.json()['result'] == 'ok'
        assert response.json()['previous']['version'] is None

    def test_insert_twice(self):
        c = Client()
        data = {'host': 'foo', 'application': 'bar', 'version': '0.0.1'}
        response = c.post('/version/', json.dumps(data),
                          content_type="application/json")
        assert response.json()['previous']['version'] is None

        data = {'host': 'foo', 'application': 'bar', 'version': '0.0.2'}
        response = c.post('/version/', json.dumps(data),
                          content_type="application/json")
        assert response.json()['previous']['version'] == '0.0.1'


class mixin(object):
    def get(self, path, method, **kwargs):
        request = self.request_factory.get(path)
        request.user = self.user
        print(method)
        response = method(request, **kwargs)
        return response

    def get_json(self, path, method, **kwargs):
        return json.loads(self.get(path, method, **kwargs).content.decode())


class BasicTests(mixin):
    """
    Requires:
    - self.url: the base url
    - self.model: the model to be used
    - self.view_list: the view method for lists
    - self.view_one: the view method for one object
    """
    def setUp(self):
        self.request_factory = RequestFactory()
        self.user = factories.UserFactory(groups=('registered',))
        self.obj = factories.get_for_model(self.model)

    def test_retrieve_object_list_as_html(self):
        response = self.get(self.url, self.view_list, mode='html')
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")

    def test_retrieve_object_as_html(self):
        response = self.get('%s/%s' % (self.url, self.obj.id),
                            self.view_one,
                            pk=self.obj.id,
                            mode='html')
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")


class RetrieveClusterByPublicAPITest(TestCase, mixin):
    def setUp(self):
        self.cluster = factories.ClusterFactory()
        self.request_factory = RequestFactory()
        self.user = factories.UserFactory(groups=('registered',))

    def test_retrieve_cluster_list_as_json(self):
        body = self.get_json('/cluster', views.cluster_list, mode='json')
        assert 'clusters' in body
        clusters = body['clusters']
        assert len(clusters) == 1
        assert clusters[0]['name'] == self.cluster.name

    def test_retrieve_cluster_list_as_html(self):
        response = self.get('/cluster', views.cluster_list, mode='html')
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")

    def test_retrieve_cluster_as_json(self):
        body = self.get_json('/cluster/%s' % self.cluster.id,
                             views.cluster,
                             mode='json',
                             pk=self.cluster.id)
        assert body is not None
        assert 'cluster' in body

    def test_retrieve_cluster_as_html(self):
        request = self.request_factory.get('/html/cluster/%s' % self.cluster.id)
        request.user = self.user
        response = views.cluster(request, self.cluster.id, mode='html')
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")



class OLDRetrieveCustomerByPublicAPITest(TestCase, mixin):
    def setUp(self):
        self.customer = factories.CustomerFactory()
        self.request_factory = RequestFactory()
        self.user = factories.UserFactory(groups=('registered',))

    def test_retrieve_customer_list_as_html(self):
        response = self.get('/html/customer', views.customer_list, mode='html')
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")

    def test_retrieve_customer_as_html(self):
        response = self.get('/html/customer/%s' % self.customer.id,
                            views.customer,
                            pk=self.customer.id,
                            mode='html')
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")


class RetrieveHostsByPublicAPITest(TestCase, mixin):
    def setUp(self):
        self.host = factories.HostFactory()
        self.request_factory = RequestFactory()
        self.user = factories.UserFactory(groups=('registered',))

    def test_retrieve_host_list_as_html(self):
        response = self.get('/html/host', views.host_list, mode='html')
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")

    def test_retrieve_host_as_html(self):
        response = self.get('/html/customer/%s' % self.host.id,
                            views.host,
                            pk=self.host.id,
                            mode='html')
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")


class RetrieveDeploymentsByPublicAPITest(TestCase, mixin):
    def setUp(self):
        self.deployment = factories.DeploymentFactory()
        self.request_factory = RequestFactory()
        self.user = factories.UserFactory(groups=('registered',))

    def test_retrieve_deployment_list_as_html(self):
        response = self.get('/html/deployment', views.deployment_list, mode='html')
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")

    def test_retrieve_deployment_as_html(self):
        response = self.get('/html/deployment/%s' % self.deployment.id,
                            views.deployment,
                            pk=self.deployment.id,
                            mode='html')
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")


class RetrieveReleasesByPublicAPITest(TestCase, mixin):
    def setUp(self):
        self.release = factories.ReleaseFactory()
        self.request_factory = RequestFactory()
        self.user = factories.UserFactory(groups=('registered',))

    def test_retrieve_release_list_as_html(self):
        response = self.get('/html/release', views.release_list, mode='html')
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")

    def test_retrieve_release_as_html(self):
        response = self.get('/html/release/%s' % self.release.id,
                            views.release,
                            pk=self.release.id,
                            mode='html')
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")
