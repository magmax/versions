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
    def get(self, path, m, **kwargs):
        request = self.request_factory.get(path)
        request.user = self.user
        response = m(request, **kwargs)
        return response

    def get_json(self, path, method, **kwargs):
        return json.loads(self.get(path, method, **kwargs).content.decode())


class BasicTests(object):
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

    def test_retrieve_object_list_as_html(self):
        request = self.request_factory.get(self.url)
        request.user = self.user
        response = self.create_list(request, mode='html')
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")

    def test_retrieve_object_as_html(self):
        obj = factories.get_for_model(self.model)
        request = self.request_factory.get('%s/%s' % (self.url, obj.id))
        request.user = self.user
        response = self.create_one(request, pk=obj.id, mode='html')
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


class RetrieveCustomerByPublicAPITest(TestCase, BasicTests):
    url = '/html/customer'
    model = models.Customer

    def setUp(self):
        BasicTests.setUp(self)

    def create_one(self, request, **kwargs):
        return views.customer(request, **kwargs)

    def create_list(self, request, **kwargs):
        return views.customer_list(request, **kwargs)


class RetrieveHostsByPublicAPITest(TestCase, BasicTests):
    url = '/html/host'
    model = models.Host

    def setUp(self):
        BasicTests.setUp(self)

    def create_one(self, request, **kwargs):
        return views.host(request, **kwargs)

    def create_list(self, request, **kwargs):
        return views.host_list(request, **kwargs)


class RetrieveDeploymentsByPublicAPITest(TestCase, BasicTests):
    url = '/html/deployment'
    model = models.Deployment

    def setUp(self):
        BasicTests.setUp(self)

    def create_one(self, request, **kwargs):
        return views.deployment(request, **kwargs)

    def create_list(self, request, **kwargs):
        return views.deployment_list(request, **kwargs)


class RetrieveReleasesByPublicAPITest(TestCase, BasicTests):
    url = '/html/release'
    model = models.Release

    def setUp(self):
        BasicTests.setUp(self)

    def create_one(self, request, **kwargs):
        return views.release(request, **kwargs)

    def create_list(self, request, **kwargs):
        return views.release_list(request, **kwargs)
