from django.db import models


class Cluster(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Host(models.Model):
    name = models.CharField(max_length=100)
    cluster = models.ForeignKey(Cluster, blank=True, null=True)

    def __str__(self):
        return self.name


class Application(models.Model):
    name = models.CharField(max_length=100)
    description = models.CharField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.name


class Version(models.Model):
    uri = models.CharField(max_length=200)
    name = models.CharField(max_length=100, blank=True, null=True)
    host = models.ForeignKey(Host, blank=True, null=True)
    application = models.ForeignKey(Application, blank=True, null=True)

    def __str__(self):
        return self.name
