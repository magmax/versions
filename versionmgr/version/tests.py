from django.test import TestCase
from django.test import Client
import json


class InsertionTest(TestCase):
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
