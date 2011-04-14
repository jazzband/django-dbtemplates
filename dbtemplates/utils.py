from django import VERSION
from django.core.cache import get_cache
from django.template import TemplateDoesNotExist
from django.utils.importlib import import_module

from django.contrib.sites.models import Site

from dbtemplates import settings


def get_cache_backend():
    return get_cache(settings.CACHE_BACKEND)

cache = get_cache_backend()


def add_default_site(instance, **kwargs):
    """
    Called via Django's signals to cache the templates, if the template
    in the database was added or changed, only if DBTEMPLATES_ADD_DEFAULT_SITE
    setting is set.
    """
    if settings.ADD_DEFAULT_SITE:
        current_site = Site.objects.get_current()
        if current_site not in instance.sites.all():
            instance.sites.add(current_site)


def get_cache_key(name):
    current_site = Site.objects.get_current()
    return 'dbtemplates::%s::%s' % (name, current_site.pk)


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


def get_loaders():
    from django.template.loader import template_source_loaders
    if template_source_loaders is None:
        try:
            from django.template.loader import (
                find_template as finder_func)
        except ImportError:
            from django.template.loader import (
                find_template_source as finder_func)
        try:
            source, name = finder_func('test')
        except TemplateDoesNotExist:
            pass
        from django.template.loader import template_source_loaders
    return template_source_loaders or []


def get_template_source(name):
    source = None
    for loader in get_loaders():
        if loader.__module__.startswith('dbtemplates.'):
            # Don't give a damn about dbtemplates' own loader.
            continue
        module = import_module(loader.__module__)
        load_template_source = getattr(module, 'load_template_source', None)
        if load_template_source is None:
            load_template_source = loader.load_template_source
        try:
            source, origin = load_template_source(name)
            if source:
                return source
        except TemplateDoesNotExist:
            pass
    if source is None and VERSION[:2] < (1, 2):
        # Django supported template source extraction still :/
        try:
            from django.template.loader import find_template_source
            template, origin = find_template_source(name, None)
            if not hasattr(template, 'render'):
                return template
        except (ImportError, TemplateDoesNotExist):
            pass
    return None
