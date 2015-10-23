# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django.utils.timezone
import django.db.models.manager
import django.contrib.sites.managers


class Migration(migrations.Migration):

    dependencies = [
        ('sites', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Template',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(help_text="Example: 'flatpages/default.html'", max_length=100, verbose_name='name')),
                ('content', models.TextField(verbose_name='content', blank=True)),
                ('creation_date', models.DateTimeField(default=django.utils.timezone.now, verbose_name='creation date')),
                ('last_changed', models.DateTimeField(default=django.utils.timezone.now, verbose_name='last changed')),
                ('sites', models.ManyToManyField(to='sites.Site', verbose_name='sites', blank=True)),
            ],
            options={
                'ordering': ('name',),
                'db_table': 'django_template',
                'verbose_name': 'template',
                'verbose_name_plural': 'templates',
            },
            managers=[
                ('objects', django.db.models.manager.Manager()),
                ('on_site', django.contrib.sites.managers.CurrentSiteManager(b'sites')),
            ],
        ),
    ]
