"""
Creates the default database template objects.
Don't know if it works.
"""

from django.dispatch import dispatcher
from django.db.models import signals
from django.contrib.sites.models import Site

from template.models import Template
from template import models as template_app

def create_default_templates(app, created_models, verbosity):
    try:
        site = Site.objects.get_current()
    except Site.DoesNotExist:
        site = None

    if site is not None:
        if Template in created_models:
            if verbosity >= 2:
                print "Creating example database templates for error 404 and error 500"

            template404 = Template(name="404.html",content="""
            {% load i18n %}<h2>{% trans 'Page not found' %}</h2>
            <p>{% trans "We're sorry, but the requested page could not be found." %}</p>""")
            template404.save()
            template404.sites.add(site)

            template500 = Template(name="500.html",content="""{% load i18n %}
            <h1>{% trans 'Server Error <em>(500)</em>' %}</h1>
            <p>{% trans "There's been an error." %}</p>""")
            template500.save()
            template500.sites.add(site)

dispatcher.connect(create_default_templates, sender=template_app, signal=signals.post_syncdb)
