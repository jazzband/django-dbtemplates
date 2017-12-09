from django.contrib.sites.models import Site
from django.db import router
from django.template import Origin, TemplateDoesNotExist
from django.template.loaders.base import Loader as BaseLoader

from dbtemplates.models import Template
from dbtemplates.utils.cache import (cache, get_cache_key,
                                     set_and_return, get_cache_notfound_key)


class Loader(BaseLoader):
    """
    A custom template loader to load templates from the database.

    Tries to load the template from the dbtemplates cache backend specified
    by the DBTEMPLATES_CACHE_BACKEND setting. If it does not find a template
    it falls back to query the database field ``name`` with the template path
    and ``sites`` with the current site.
    """
    is_usable = True

    def get_template_sources(self, template_name, template_dirs=None):
        yield Origin(
            name=template_name,
            template_name=template_name,
            loader=self,
        )

    def get_contents(self, origin):
        content, _ = self._load_template_source(origin.template_name)
        return content

    def _load_and_store_template(self, template_name, cache_key, site, **params):
        template = Template.objects.get(name__exact=template_name, **params)
        db = router.db_for_read(Template, instance=template)
        display_name = 'dbtemplates:%s:%s:%s' % (db, template_name, site.domain)
        return set_and_return(cache_key, template.content, display_name)

    def _load_template_source(self, template_name, template_dirs=None):
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
        cache_key = get_cache_key(template_name)
        if cache:
            try:
                backend_template = cache.get(cache_key)
                if backend_template:
                    return backend_template, template_name
            except Exception:
                pass

        # Not found in cache, move on.
        cache_notfound_key = get_cache_notfound_key(template_name)
        if cache:
            try:
                notfound = cache.get(cache_notfound_key)
                if notfound:
                    raise TemplateDoesNotExist(template_name)
            except Exception:
                raise TemplateDoesNotExist(template_name)

        # Not marked as not-found, move on...

        try:
            return self._load_and_store_template(template_name, cache_key,
                                                site, sites__in=[site.id])
        except (Template.MultipleObjectsReturned, Template.DoesNotExist):
            try:
                return self._load_and_store_template(template_name, cache_key,
                                                    site, sites__isnull=True)
            except (Template.MultipleObjectsReturned, Template.DoesNotExist):
                pass

        # Mark as not-found in cache.
        cache.set(cache_notfound_key, '1')
        raise TemplateDoesNotExist(template_name)
