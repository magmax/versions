from django.db import models


class Cluster(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

    def ordered_attributes(self):
        return self.attributes.order_by('name')


class ClusterAttribute(models.Model):
    name = models.CharField(max_length=100)
    value = models.TextField()
    cluster = models.ForeignKey(Cluster, related_name="attributes")

    def __str__(self):
        return self.name


class Host(models.Model):
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=100, blank=True, null=True)
    cluster = models.ForeignKey(
        Cluster,
        blank=True,
        null=True,
        related_name="hosts",
    )

    def __str__(self):
        return self.name


class HostAttribute(models.Model):
    name = models.CharField(max_length=100)
    value = models.TextField()
    host = models.ForeignKey(Host, related_name="attributes")

    def __str__(self):
        return self.name


class Deployment(models.Model):
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.label or self.name


class DeploymentAttribute(models.Model):
    name = models.CharField(max_length=100)
    value = models.TextField()
    deployment = models.ForeignKey(Deployment, related_name="attributes")

    def __str__(self):
        return self.name


class Application(models.Model):
    name = models.CharField(max_length=100)
    label = models.CharField(max_length=100, blank=True, null=True)
    description = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name


class ApplicationAttribute(models.Model):
    name = models.CharField(max_length=100)
    value = models.TextField()
    application = models.ForeignKey(Application, related_name="attributes")

    def __str__(self):
        return self.name


class Version(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return self.name


class Service(models.Model):
    version = models.ForeignKey(Version, related_name="services")
    host = models.ForeignKey(Host, related_name="services")
    application = models.ForeignKey(Application, related_name="services")
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


class CustomerAttribute(models.Model):
    name = models.CharField(max_length=100)
    value = models.TextField()
    customer = models.ForeignKey(Customer, related_name="attributes")

    def __str__(self):
        return self.name


class Release(models.Model):
    name = models.CharField(max_length=100)
    services = models.ManyToManyField(Service, related_name="releases")

    def __str__(self):
        return self.name


class ReleaseAttribute(models.Model):
    name = models.CharField(max_length=100)
    value = models.TextField()
    release = models.ForeignKey(Release, related_name="attributes")

    def __str__(self):
        return self.name
