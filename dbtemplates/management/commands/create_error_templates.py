from optparse import make_option

from django.core.management.base import CommandError, NoArgsCommand
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

class Command(NoArgsCommand):
    help = "Creates the 404.html and 500.html error templates as database template objects."
    option_list = NoArgsCommand.option_list + (
        make_option("-f", "--force", action="store_true", dest="force",
            default=False, help="overwrite existing database templates"),
    )
    def handle_noargs(self, **options):
        force = options.get('force')
        try:
            site = Site.objects.get_current()
        except Site.DoesNotExist:
            raise CommandError("Please make sure to have the sites contrib "
                               "app installed and setup with a site object")
        for error_code in (404, 500):
            template, created = Template.objects.get_or_create(
                name="%s.html" % error_code)
            if created or (not created and force):
                template.content = TEMPLATES.get(error_code, '')
                template.save()
                template.sites.add(site)
                print "Created database template for %s errors." % error_code
            else:
                print "A template for %s errors already exists." % error_code
