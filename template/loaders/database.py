from django.template import TemplateDoesNotExist
from django.contrib.sites.models import Site
from django.conf import settings
from template.models import Template

try:
    site = Site.objects.get_current()
except:
    site = None

def load_template_source(template_name, template_dirs=None):
    """
    Loader which fetches the template content from the database depending on
    the current ``Site``.
    """
    if site is not None:
        try:
            t = Template.objects.get(name__exact=template_name, sites__pk=site.id)
            return (t.content, 'db:%s:%s' % (settings.DATABASE_ENGINE, template_name))
        except:
            pass
    raise TemplateDoesNotExist, template_name
load_template_source.is_usable = True
