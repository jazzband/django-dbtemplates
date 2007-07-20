from django.conf import settings
from django.template import TemplateDoesNotExist
from django.contrib.sites.models import Site

from dbtemplates.models import Template

try:
    site = Site.objects.get_current()
except:
    site = None

def load_template_source(template_name, template_dirs=None):
    """
    Loads templates from the database by querying the database field ``name``
    with a template path and ``sites`` with the current site.
    """
    if site is not None:
        try:
            t = Template.objects.get(name__exact=template_name, sites__pk=site.id)
            return (t.content, 'db:%s:%s' % (settings.DATABASE_ENGINE, template_name))
        except:
            pass
    raise TemplateDoesNotExist, template_name
load_template_source.is_usable = True