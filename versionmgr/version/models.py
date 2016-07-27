from django.db import models


class Cluster(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class ClusterAttribute(models.Model):
    name = models.CharField(max_length=100)
    value = models.TextField()
    cluster = models.ForeignKey(Cluster, related_name="attributes")

    def __str__(self):
        return self.name


class Host(models.Model):
    name = models.CharField(max_length=100)
    cluster = models.ForeignKey(Cluster, blank=True, null=True, related_name="hosts")

    def __str__(self):
        return self.name


class HostAttribute(models.Model):
    name = models.CharField(max_length=100)
    value = models.TextField()
    host = models.ForeignKey(Host, related_name="attributes")

    def __str__(self):
        return self.name


class Application(models.Model):
    name = models.CharField(max_length=100)
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
    uri = models.CharField(max_length=200)
    name = models.CharField(max_length=100, blank=True, null=True)
    host = models.ForeignKey(Host, blank=True, null=True)
    application = models.ForeignKey(Application, blank=True, null=True)
    updated = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name
