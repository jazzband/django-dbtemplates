# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('dbtemplates', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='template',
            name='category',
            field=models.CharField(
                help_text=(
                    'The category for this template, useful '
                    'if you want to organize your templates.'
                ),
                max_length=50, verbose_name='category', default='', blank=True
            ),
        ),
        migrations.AddField(
            model_name='template',
            name='title',
            field=models.CharField(
                help_text='The title of this template, used for display only.',
                max_length=100, verbose_name='title', default='', blank=True
            ),
        ),
    ]
