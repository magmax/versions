from django.contrib import admin

from . import models


class ApplicationAttributeInline(admin.TabularInline):
    model = models.ApplicationAttribute


class ClusterAttributeInline(admin.TabularInline):
    model = models.ClusterAttribute


class HostAttributeInline(admin.TabularInline):
    model = models.HostAttribute


class HostInline(admin.TabularInline):
    model = models.Host


class DeploymentInline(admin.TabularInline):
    model = models.Deployment


class ServiceInline(admin.TabularInline):
    model = models.Service


class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('name', 'description')
    inlines = [
        ApplicationAttributeInline,
    ]


class ClusterAdmin(admin.ModelAdmin):
    inlines = [
        HostInline,
        ClusterAttributeInline,
    ]


class HostAdmin(admin.ModelAdmin):
    inlines = [
        ServiceInline,
        HostAttributeInline,
    ]


admin.site.register(models.Cluster, ClusterAdmin)
admin.site.register(models.Host, HostAdmin)
admin.site.register(models.Application, ApplicationAdmin)
admin.site.register(models.Version)
admin.site.register(models.Deployment)
admin.site.register(models.Service)
admin.site.register(models.ClusterAttribute)
admin.site.register(models.HostAttribute)
admin.site.register(models.ApplicationAttribute)
