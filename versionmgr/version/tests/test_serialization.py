from django.test import SimpleTestCase
import json

from . import factories
from version import views


class ClusterSerializationTest(SimpleTestCase):
    def setUp(self):
        self.cluster = factories.ClusterFactory.build()
        self.clusterview = views.ClusterView.from_model(self.cluster)

    def test_basic_model_load(self):
        assert self.clusterview.id == self.cluster.id
        assert self.clusterview.name == self.cluster.name

    def test_two_objects_are_different(self):
        cluster2 = factories.ClusterFactory.build()
        clusterview2 = views.ClusterView.from_model(cluster2)
        assert self.clusterview.name != clusterview2.name

    def test_basic_serialization(self):
        clusterjson = self.clusterview.to_json()
        clusterdict = json.loads(clusterjson)
        assert clusterdict['id'] == self.clusterview.id
        assert clusterdict['name'] == self.clusterview.name

    def test_basic_deserialization(self):
        clusterjson = self.clusterview.to_json()
        print (clusterjson)
        cluster2 = views.ClusterView.from_json(clusterjson)
        assert self.cluster.id == cluster2.id
        assert self.cluster.name == cluster2.name


class HostSerializationTest(SimpleTestCase):
    def setUp(self):
        self.host = factories.HostFactory.build()
        self.hostview = views.HostView.from_model(self.host)

    def test_basic_model_load(self):
        assert self.hostview.id == self.host.id
        assert self.hostview.name == self.host.name
        assert self.hostview.label == self.host.label

    def test_basic_serialization(self):
        hostjson = self.hostview.to_json()
        hostdict = json.loads(hostjson)
        assert hostdict['id'] == self.hostview.id
        assert hostdict['name'] == self.hostview.name
        assert hostdict['label'] == self.hostview.label

    def test_basic_deserialization(self):
        hostjson = self.hostview.to_json()
        host2 = views.HostView.from_json(hostjson)
        assert self.host.id == host2.id
        assert self.host.name == host2.name
        assert self.host.label == host2.label
