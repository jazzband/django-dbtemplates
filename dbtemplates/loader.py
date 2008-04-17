import os
from django.conf import settings
from django.dispatch import dispatcher
from django.db.models import signals
from django.template import TemplateDoesNotExist
from django.contrib.sites.models import Site

from dbtemplates.models import Template

try:
    site = Site.objects.get_current()
except:
    site = None

try:
    cache_dir = os.path.normpath(getattr(settings, 'DBTEMPLATES_CACHE_DIR', None))
    if not os.path.isdir(cache_dir):
        raise
except:
    cache_dir = None
    
def load_template_source(template_name, template_dirs=None):
    """
    Loads templates from the database by querying the database field ``name``
    with a template path and ``sites`` with the current site.
    """
    if site is not None:
        if cache_dir is not None:
            filepath = os.path.join(cache_dir, template_name)
        try:
            return (open(filepath).read(), filepath)
        except IOError:
            try:
                t = Template.objects.get(name__exact=template_name, sites__pk=site.id)
                try:
                    f = open(filepath, 'w')
                    f.write(t.content)
                    f.close()
                except IOError:
                        pass
                return (t.content, 'db:%s:%s' % (settings.DATABASE_ENGINE, template_name))
            except:
                pass
    raise TemplateDoesNotExist, template_name
load_template_source.is_usable = True

def remove_cached_template(instance):
    try:
        filepath = os.path.join(cache_dir, instance.name)
        os.remove(filepath)
    except OSError:
        pass

dispatcher.connect(remove_cached_template, sender=Template, signal=signals.post_save)
dispatcher.connect(remove_cached_template, sender=Template, signal=signals.pre_delete)

