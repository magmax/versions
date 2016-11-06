from __future__ import absolute_import, unicode_literals
import json
from celery import shared_task

from version import models

@shared_task
def save_version(request_body, meta):
    data = json.loads(request_body)
    host, _ = models.Host.objects.get_or_create(
        name=data.get('host') or meta['REMOTE_HOST']
    )
    app, _ = models.Application.objects.get_or_create(
        name=data['application']
    )
    version, _ = models.Version.objects.get_or_create(
        name=data['version']
    )
    deployment, _ = models.Deployment.objects.get_or_create(
        name=data.get('deployment', "default")
    )
    component, _ = models.Component.objects.get_or_create(
        version=version,
        application=app,
    )

    service, created = models.Service.objects.get_or_create(
        host=host,
        deployment=deployment,
        defaults=dict(
            component=component,
            arguments=data.get('arguments'),
        )

    )
    prev_version = None if created else service.component.version.name
    service.component = component
    service.save()
