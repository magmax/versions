from django.test import TestCase
from django.test import Client
import json

from . import factories


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
        response = self.client.get('/html/cluster/%s' % self.cluster.id)
        assert response.status_code == 200
        assert 'text/html' in response.get("content-type")
