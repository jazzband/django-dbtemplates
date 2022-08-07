import sys
from django.core.management.base import CommandError, BaseCommand
from django.contrib.sites.models import Site

from dbtemplates.models import Template

TEMPLATES = {
    404: """
{% extends "base.html" %}
{% load i18n %}
{% block content %}
<h2>{% trans 'Page not found' %}</h2>
<p>{% trans "We're sorry, but the requested page could not be found." %}</p>
{% endblock %}
""",
    500: """
{% extends "base.html" %}
{% load i18n %}
{% block content %}
<h1>{% trans 'Server Error <em>(500)</em>' %}</h1>
<p>{% trans "There's been an error." %}</p>
{% endblock %}
""",
}


class Command(BaseCommand):
    help = "Creates the default error templates as database template objects."

    def add_arguments(self, parser):
        parser.add_argument(
            "-f", "--force", action="store_true", dest="force",
            default=False, help="overwrite existing database templates")

    def handle(self, **options):
        force = options.get('force')
        try:
            site = Site.objects.get_current()
        except Site.DoesNotExist:
            raise CommandError("Please make sure to have the sites contrib "
                               "app installed and setup with a site object")

        verbosity = int(options.get('verbosity', 1))
        for error_code in (404, 500):
            template, created = Template.objects.get_or_create(
                name=f"{error_code}.html")
            if created or (not created and force):
                template.content = TEMPLATES.get(error_code, '')
                template.save()
                template.sites.add(site)
                if verbosity >= 1:
                    sys.stdout.write("Created database template "
                                     "for %s errors.\n" % error_code)
            else:
                if verbosity >= 1:
                    sys.stderr.write("A template for %s errors "
                                     "already exists.\n" % error_code)
