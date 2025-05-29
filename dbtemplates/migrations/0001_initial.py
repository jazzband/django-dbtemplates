import django
import django.utils.timezone
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("sites", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Template",
            fields=[
                (
                    "id",
                    models.AutoField(
                        verbose_name="ID",
                        serialize=False,
                        auto_created=True,
                        primary_key=True,
                    ),
                ),
                (
                    "name",
                    models.CharField(
                        help_text="Example: 'flatpages/default.html'",
                        max_length=100,
                        verbose_name="name",
                    ),
                ),
                (
                    "content",
                    models.TextField(verbose_name="content", blank=True),
                ),  # noqa
                (
                    "creation_date",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="creation date",  # noqa
                    ),
                ),
                (
                    "last_changed",
                    models.DateTimeField(
                        default=django.utils.timezone.now,
                        verbose_name="last changed",  # noqa
                    ),
                ),
                (
                    "sites",
                    models.ManyToManyField(
                        to="sites.Site", verbose_name="sites", blank=True,
                        related_name='%(class)s_set', related_query_name='%(class)s',
                    ),
                ),
            ],
            options={
                "ordering": ("name",),
                "db_table": "django_template",
                "verbose_name": "template",
                "verbose_name_plural": "templates",
            },
            bases=(models.Model,),
            managers=[
                ("objects", django.db.models.manager.Manager()),
                (
                    "on_site",
                    django.contrib.sites.managers.CurrentSiteManager("sites"),
                ),  # noqa
            ],
        ),
    ]
