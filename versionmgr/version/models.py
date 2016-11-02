from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.contrib.contenttypes.models import ContentType


class Attribute(models.Model):
    name = models.CharField(max_length=100)
    value = models.TextField()

    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    def __str__(self):
        return self.name


class Cluster(models.Model):
    name = models.CharField(max_length=100)
    attributes = GenericRelation(Attribute)

    def __str__(self):
        return self.name

    def ordered_attributes(self):
        return self.attributes.order_by('name')


class Host(models.Model):
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=100, blank=True, null=True)
    cluster = models.ForeignKey(
        Cluster,
        blank=True,
        null=True,
        related_name="hosts",
    )
    attributes = GenericRelation(Attribute)

    def __str__(self):
        return self.name


class Deployment(models.Model):
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.label or self.name


class Application(models.Model):
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)
    attributes = GenericRelation(Attribute)

    def __str__(self):
        return self.name


class Version(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        permissions = (
            ('view_version', 'Can see version data'),
        )


class Component(models.Model):
    version = models.ForeignKey(Version, related_name="components")
    application = models.ForeignKey(Application, related_name="components")

    def __str__(self):
        return self.name


class Service(models.Model):
    host = models.ForeignKey(Host, related_name="services")
    component = models.ForeignKey(Component, related_name="services")
    arguments = models.TextField(blank=True, null=True)
    deployment = models.ForeignKey(
        Deployment, related_name="services", blank=True, null=True)

    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s (%s) at %s/%s" % (
            self.application,
            self.version,
            self.host,
            self.deployment,
        )


class Customer(models.Model):
    name = models.CharField(max_length=100)
    deployments = models.ManyToManyField(Deployment, related_name="customers")
    def __str__(self):
        return self.name


class Product(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Release(models.Model):
    name = models.CharField(max_length=100)
    services = models.ManyToManyField(Service, related_name="releases")

    def __str__(self):
        return self.name
