# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-07 14:52
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('version', '0014_auto_20161002_0640'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='version',
            options={'permissions': (('view_version', 'Can see version'),)},
        ),
    ]
