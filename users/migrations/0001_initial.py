# -*- coding: utf-8 -*-
# Generated by Django 1.9.4 on 2016-04-01 20:35
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Profile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gender', models.CharField(choices=[('Male', 'Man'), ('Female', 'Woman'), ('Other', 'Other')], default='Male', max_length=8)),
                ('age', models.CharField(choices=[('Under 18', 'Under 16'), ('18-19', '18-19'), ("20's", "20's"), ("30's", "30's"), ("40's", "40's"), ("50's", "50's"), ('60+', '60+')], max_length=8)),
                ('wants_texts', models.BooleanField(default=False)),
                ('phone_number', models.CharField(blank=True, max_length=15, null=True)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]