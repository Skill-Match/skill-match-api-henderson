# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-01 19:27
from __future__ import unicode_literals

import django.contrib.gis.db.models.fields
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('skill_match', '0002_auto_20160330_2233'),
    ]

    operations = [
        migrations.AddField(
            model_name='hendersonpark',
            name='location',
            field=django.contrib.gis.db.models.fields.PointField(blank=True, null=True, srid=4326),
        ),
    ]