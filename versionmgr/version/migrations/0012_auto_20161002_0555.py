# -*- coding: utf-8 -*-
# Generated by Django 1.10 on 2016-10-02 05:55
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('version', '0011_auto_20161001_0816'),
    ]

    operations = [
        migrations.CreateModel(
            name='Release',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('services', models.ManyToManyField(related_name='releases', to='version.Service')),
            ],
        ),
        migrations.CreateModel(
            name='ReleaseAttribute',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100)),
                ('value', models.TextField()),
                ('release', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='attributes', to='version.Release')),
            ],
        ),
        migrations.RenameField(
            model_name='customerattribute',
            old_name='application',
            new_name='customer',
        ),
    ]