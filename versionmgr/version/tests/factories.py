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
