from django.test import TestCase
from django.test import Client
import json

from . import factories

class InsertionByPublicAPITest(TestCase):
    def test_basic_insertion(self):
        c = Client()
        response = c.post('/version/', json.dumps({'host': 'foo', 'application': 'bar', 'version': '1.2.3.4'}), content_type="application/json")

        assert response.status_code == 200
        assert response.json()['result'] == 'ok'
        assert response.json()['previous']['version'] is None

    def test_insert_twice(self):
        c = Client()
        response = c.post('/version/', json.dumps({'host': 'foo', 'application': 'bar', 'version': '0.0.1'}), content_type="application/json")
        assert response.json()['previous']['version'] is None

        response = c.post('/version/', json.dumps({'host': 'foo', 'application': 'bar', 'version': '0.0.2'}), content_type="application/json")
        assert response.json()['previous']['version'] == '0.0.1'


class RetrieveByPublicAPITest(TestCase):
    def test_retrieve_cluster_list(self):
        cluster = factories.ClusterFactory()

        c = Client()
        response = c.get('/cluster/', content_type="application/json")
        body = response.json()
        assert 'clusters' in body
        clusters = body['clusters']
        assert len(clusters) == 1
        assert clusters[0]['name'] == cluster.name

    def test_retrieve_cluster(self):
        cluster = factories.ClusterFactory()

        c = Client()
        response = c.get('/cluster/%s' % cluster.id, content_type="application/json")
        body = response.json()
