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
    deployment = models.ForeignKey(Deployment, related_name="deployment")

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


class AppInstance(models.Model):
    version = models.ForeignKey(Version, related_name="app_instances")
    host = models.ForeignKey(Host, related_name="app_instances")
    application = models.ForeignKey(Application, related_name="app_instances")
    deployment = models.ForeignKey(
        Deployment, related_name="app_instances", blank=True, null=True)

    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "%s (%s) at %s/%s" % (
            self.application,
            self.version,
            self.host,
            self.deployment,
        )
