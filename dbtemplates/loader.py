import os
from django.conf import settings
from django.template import TemplateDoesNotExist
from django.core.exceptions import ImproperlyConfigured

from dbtemplates.models import Template, backend

def load_template_source(template_name, template_dirs=None):
    """
    Tries to load the template from DBTEMPLATES_CACHE_DIR. If it does not
    exist loads templates from the database by querying the database field
    ``name`` with a template path and ``sites`` with the current site,
    and tries to save the template as DBTEMPLATES_CACHE_DIR/``name`` for
    subsequent requests. If DBTEMPLATES_CACHE_DIR is not configured falls
    back to database-only operation.
    """
    display_name = 'db:%s:%s' % (settings.DATABASE_ENGINE, template_name)
    if backend:
        try:
            backend_template = backend.load(template_name)
            if backend_template is not None:
                return backend_template, template_name
        except:
            pass
    try:
        template = Template.objects.get(name__exact=template_name,
                                        sites__pk=settings.SITE_ID)
        return (template.content, display_name)
    except:
        pass
    raise TemplateDoesNotExist, template_name
load_template_source.is_usable = True
