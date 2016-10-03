import factory
from faker import Factory as FakerFactory

from version import models

faker = FakerFactory.create()
faker.seed(1234)


class ClusterFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Cluster

    name = factory.LazyAttribute(lambda x: faker.first_name_female())


class HostFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Host

    name = factory.LazyAttribute(lambda x: faker.last_name())
    label = factory.LazyAttribute(lambda x: 'label %s' % x.name)
    cluster = factory.SubFactory(ClusterFactory)


class CustomerFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Customer

    name = factory.LazyAttribute(lambda x: faker.company())


class DeploymentFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Deployment

    name = factory.LazyAttribute(lambda x: faker.color_name())
    label = factory.LazyAttribute(lambda x: 'label %s' % x.name)


class ReleaseFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = models.Release

    name = factory.LazyAttribute(lambda x: faker.color_name())
