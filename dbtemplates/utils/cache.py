from django.core.cache import get_cache

from django.contrib.sites.models import Site

from dbtemplates.conf import settings


def get_cache_backend():
    if hasattr(settings, "CACHES") and "dbtemplates" in settings.CACHES:
        backend = settings.CACHES["dbtemplates"]["BACKEND"]
        return get_cache(backend)
    return get_cache()

cache = get_cache_backend()


def get_cache_key(name):
    current_site = Site.objects.get_current()
    return 'dbtemplates::%s::%s' % (name, current_site.pk)


def set_and_return(cache_key, content, display_name):
    # Save in cache backend explicitly if manually deleted or invalidated
    if cache:
        cache.set(cache_key, content)
    return (content, display_name)


def add_template_to_cache(instance, **kwargs):
    """
    Called via Django's signals to cache the templates, if the template
    in the database was added or changed.
    """
    remove_cached_template(instance)
    cache.set(get_cache_key(instance.name), instance.content)


def remove_cached_template(instance, **kwargs):
    """
    Called via Django's signals to remove cached templates, if the template
    in the database was changed or deleted.
    """
    cache.delete(get_cache_key(instance.name))
