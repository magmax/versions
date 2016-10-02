# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


def create_components(apps, schema_editor):
    db_alias = schema_editor.connection.alias

    Service = apps.get_model('version', 'Service')
    Component = apps.get_model('version', 'Component')
    for service in Service.objects.using(db_alias).all():
        component, _ = Component.objects.using(db_alias).get_or_create(
            version = service.version,
            application = service.application,
        )
        service.component = component
        service.save()


class Migration(migrations.Migration):

    dependencies = [
        ('version', '0013_component_product_productattribute'),
    ]

    operations = [
        migrations.AddField(
            model_name='service',
            name='component',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='services', to='version.Component'),
        ),
        migrations.RunPython(
            create_components
        ),
        migrations.AlterField(
            model_name='service',
            name='component',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='services', to='version.Component'),
            preserve_default=False,
        ),
        migrations.RemoveField(
            model_name='service',
            name='application',
        ),
        migrations.RemoveField(
            model_name='service',
            name='version',
        ),
    ]
