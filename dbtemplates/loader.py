from django.contrib.sites.models import Site
from django.template import TemplateDoesNotExist

from dbtemplates.conf import settings
from dbtemplates.models import Template
from dbtemplates.utils.cache import (cache, get_cache_key,
                                     set_and_return, get_cache_notfound_key)
from django.template.loader import BaseLoader


class Loader(BaseLoader):
    """
    A custom template loader to load templates from the database.

    Tries to load the template from the dbtemplates cache backend specified
    by the DBTEMPLATES_CACHE_BACKEND setting. If it does not find a template
    it falls back to query the database field ``name`` with the template path
    and ``sites`` with the current site.
    """
    is_usable = True

    def load_template_source(self, template_name, template_dirs=None):
        # The logic should work like this:
        # * Try to find the template in the cache. If found, return it.
        # * Now check the cache if a lookup for the given template
        #   has failed lately and hand over control to the next template
        #   loader waiting in line.
        # * If this still did not fail we first try to find a site-specific
        #   template in the database.
        # * On a failure from our last attempt we try to load the global
        #   template from the database.
        # * If all of the above steps have failed we generate a new key
        #   in the cache indicating that queries failed, with the current
        #   timestamp.
        site = Site.objects.get_current()
        display_name = 'dbtemplates:%s:%s:%s' % (settings.DATABASE_ENGINE,
                                                 template_name, site.domain)
        cache_key = get_cache_key(template_name)
        if cache:
            try:
                backend_template = cache.get(cache_key)
                if backend_template:
                    return backend_template, template_name
            except:
                pass

        # Not found in cache, move on.
        cache_notfound_key = get_cache_notfound_key(template_name)
        if cache:
            try:
                notfound = cache.get(cache_notfound_key)
                if notfound:
                    raise TemplateDoesNotExist(template_name)
            except:
                raise TemplateDoesNotExist(template_name)

        # Not marked as not-found, move on...

        try:
            template = Template.objects.get(name__exact=template_name,
                                            sites__in=[site.id])
            return set_and_return(cache_key, template.content, display_name)
        except (Template.MultipleObjectsReturned, Template.DoesNotExist):
            try:
                template = Template.objects.get(name__exact=template_name)
                return set_and_return(cache_key, template.content, display_name)
            except Template.DoesNotExist:
                pass

        # Mark as not-found in cache.
        cache.set(cache_notfound_key, '1')
        raise TemplateDoesNotExist(template_name)
