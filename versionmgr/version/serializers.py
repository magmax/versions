from rest_framework import serializers
from generic_relations.relations import GenericRelatedField
from generic_relations.serializers import GenericModelSerializer
from django.contrib.auth.models import User

from version import models


class AttributeSerializer(serializers.ModelSerializer):
    class Meta:
        model = models.Attribute
        fields = ('id', 'name', 'value')

    def create(self, validated_data):
        return models.Cluster.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.value = validated_data.get('value', instance.value)
        instance.save()
        return instance


class ClusterSerializer(serializers.HyperlinkedModelSerializer):
    attributes = AttributeSerializer(many=True, read_only=True)

    class Meta:
        model = models.Cluster
        fields = ('url', 'id', 'name', 'attributes')

    def create(self, validated_data):
        return models.Cluster.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


class HostSerializer(serializers.HyperlinkedModelSerializer):
    attributes = AttributeSerializer(many=True, read_only=True)

    class Meta:
        model = models.Host
        fields = ('url', 'id', 'name', 'label', 'attributes')

    def create(self, validated_data):
        return models.Cluster.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.label = validated_data.get('label', instance.label)
        instance.save()
        return instance


class DeploymentSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Deployment
        fields = ('url', 'id', 'name', 'label')

    def create(self, validated_data):
        return models.Cluster.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.label = validated_data.get('label', instance.label)
        instance.save()
        return instance


class ApplicationSerializer(serializers.HyperlinkedModelSerializer):
    attributes = AttributeSerializer(many=True, read_only=True)

    class Meta:
        model = models.Application
        fields = ('url', 'id', 'name', 'label', 'description', 'attributes')

    def create(self, validated_data):
        return models.Cluster.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.label = validated_data.get('label', instance.label)
        instance.description = validated_data.get('description', instance.description)
        instance.save()
        return instance


class VersionSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = models.Version
        fields = ('url', 'id', 'name')

    def create(self, validated_data):
        return models.Cluster.objects.create(**validated_data)

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.save()
        return instance


class ComponentSerializer(serializers.HyperlinkedModelSerializer):
    application = ApplicationSerializer(many=False, read_only=True)
    version = VersionSerializer(many=False, read_only=True)

    class Meta:
        model = models.Component
        fields = ('url', 'id', 'application', 'version')


class ServiceSerializer(serializers.HyperlinkedModelSerializer):
    component = ComponentSerializer(many=False, read_only=True)
    class Meta:
        model = models.Service
        fields = ('url', 'id', 'updated', 'arguments', 'component')


class ClusterWithDepsSerializer(ClusterSerializer):
    hosts = HostSerializer(many=True, read_only=True)

    class Meta:
        model = models.Cluster
        fields = ('url', 'id', 'name', 'hosts', 'attributes')
        depth = 1


class HostWithDepsSerializer(HostSerializer):
    cluster = ClusterSerializer(many=False, read_only=True)

    class Meta:
        model = models.Host
        fields = ('url', 'id', 'name', 'label', 'attributes', 'cluster',)
        depth = 1


class DeploymentWithDepsSerializer(HostSerializer):
    class Meta:
        model = models.Deployment
        fields = ('url', 'id', 'name', 'label',)
        depth = 1


class ApplicationWithDepsSerializer(HostSerializer):
    components = ComponentSerializer(many=True, read_only=True)
    class Meta:
        model = models.Application
        fields = ('url', 'id', 'name', 'label', 'description', 'attributes', 'components')
        depth = 1


class VersionWithDepsSerializer(HostSerializer):
    components = ComponentSerializer(many=True, read_only=True)
    services = ServiceSerializer(many=True, read_only=True)

    class Meta:
        model = models.Version
        fields = ('url', 'id', 'name', 'components', 'services')
        depth = 1


class ComponentWithDepsSerializer(HostSerializer):
    application = ApplicationWithDepsSerializer(many=False, read_only=True)
    version = VersionWithDepsSerializer(many=False, read_only=True)

    class Meta:
        model = models.Component
        fields = ('url', 'id', 'application', 'version', 'services')
        depth = 1


class ServiceWithDepsSerializer(serializers.HyperlinkedModelSerializer):
    host = HostSerializer(many=False, read_only=True)
    component = ComponentSerializer(many=False, read_only=True)
    version = VersionSerializer(many=False, read_only=True)
    deployment = DeploymentSerializer(many=False, read_only=True)

    class Meta:
        model = models.Service
        fields = ('url', 'id', 'updated', 'arguments', 'host', 'component', 'version', 'deployment')


class AttributeListSerializer(serializers.ModelSerializer):
    tagged_object = GenericRelatedField(
        {
            models.Cluster: ClusterSerializer(),
            models.Host: HostSerializer()
        },

    )

    class Meta:
        model = models.Attribute
        fields = ('id', 'name', 'value', )
