from django.test import TestCase, RequestFactory
from django.test import Client
from django.contrib.auth.models import AnonymousUser, User

import json

from . import factories
from version import views


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


class RetrieveClusterByPublicAPITest(TestCase):
    def setUp(self):
        self.cluster = factories.ClusterFactory()
        self.client = Client()
        self.request_factory = RequestFactory()
        self.user = factories.UserFactory(groups=('registered',))

    def test_retrieve_cluster_list_as_json(self):
        response = self.client.get('/cluster/')
        body = response.json()
        assert 'clusters' in body
        clusters = body['clusters']
        assert len(clusters) == 1
        assert clusters[0]['name'] == self.cluster.name

    def test_retrieve_cluster_list_as_html(self):
        response = self.client.get('/html/cluster')
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")

    def test_retrieve_cluster_as_json(self):
        response = self.client.get('/cluster/%s' % self.cluster.id)
        body = response.json()
        assert body is not None

    def test_retrieve_cluster_as_html(self):
        request = self.request_factory.get('/html/cluster/%s' % self.cluster.id)
        request.user = self.user
        response = views.cluster(request, self.cluster.id, mode='html')
        print(self.user.has_perm('view_version'))
        print(self.user.groups.first().permissions.all())
        print(User.objects.get(id=self.user.id).has_perm('view_version'))
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")


class RetrieveCustomerByPublicAPITest(TestCase):
    def setUp(self):
        self.customer = factories.CustomerFactory()
        self.client = Client()

    def test_retrieve_customer_list_as_html(self):
        response = self.client.get('/html/customer')
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")

    def test_retrieve_customer_as_html(self):
        response = self.client.get('/html/customer/%s' % self.customer.id)
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")


class RetrieveHostsByPublicAPITest(TestCase):
    def setUp(self):
        self.host = factories.HostFactory()
        self.client = Client()

    def test_retrieve_customer_list_as_html(self):
        response = self.client.get('/html/host')
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")

    def test_retrieve_customer_as_html(self):
        response = self.client.get('/html/host/%s' % self.host.id)
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")


class RetrieveDeploymentsByPublicAPITest(TestCase):
    def setUp(self):
        self.deployment = factories.DeploymentFactory()
        self.client = Client()

    def test_retrieve_deployment_list_as_html(self):
        response = self.client.get('/html/deployment')
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")

    def test_retrieve_deployment_as_html(self):
        response = self.client.get('/html/deployment/%s' % self.deployment.id)
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")


class RetrieveReleasesByPublicAPITest(TestCase):
    def setUp(self):
        self.release = factories.ReleaseFactory()
        self.client = Client()

    def test_retrieve_release_list_as_html(self):
        response = self.client.get('/html/release')
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")

    def test_retrieve_release_as_html(self):
        response = self.client.get('/html/release/%s' % self.release.id)
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")
