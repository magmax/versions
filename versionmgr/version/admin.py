from django.contrib import admin

from . import models


class HostInline(admin.TabularInline):
    model = models.Host


class DeploymentInline(admin.TabularInline):
    model = models.Deployment


class ServiceInline(admin.TabularInline):
    model = models.Service


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')

class ClusterAdmin(admin.ModelAdmin):
    inlines = [
        HostInline,
    ]


class HostAdmin(admin.ModelAdmin):
    inlines = [
        ServiceInline,
    ]


admin.site.register(models.Cluster, ClusterAdmin)
admin.site.register(models.Host, HostAdmin)
admin.site.register(models.Application, ApplicationAdmin)
admin.site.register(models.Version)
admin.site.register(models.Deployment)
admin.site.register(models.Service)
admin.site.register(models.Attribute)
admin.site.register(models.Customer)
