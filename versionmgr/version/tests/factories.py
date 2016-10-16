import factory
from faker import Factory as FakerFactory

from version import models
from django.contrib import auth


faker = FakerFactory.create()
faker.seed(1234)


class UserFactory(factory.django.DjangoModelFactory):
    class Meta:
        model = auth.models.User

    username = factory.LazyAttribute(lambda x: faker.first_name())
    email = factory.LazyAttribute(lambda x: faker.email())

    @factory.post_generation
    def groups(self, create, extracted, **kwargs):
        if not create:
            # Simple build, do nothing.
            return

        if extracted:
            for group in extracted:
                if isinstance(group, str):
                    grp = auth.models.Group.objects.get(name=group)
                    self.groups.add(grp)
                    if group == 'registered':
                        perm = auth.models.Permission.objects.get(codename="view_version")
                        grp.permissions.add(perm)
                        grp.save()
                else:
                    self.groups.add(group)


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
