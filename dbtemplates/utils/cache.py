from django.core.cache import get_cache

from django.contrib.sites.models import Site
from django.template.defaultfilters import slugify

from dbtemplates.conf import settings


def get_cache_backend():
    return get_cache(settings.DBTEMPLATES_CACHE_BACKEND)

cache = get_cache_backend()


def get_cache_key(name, site_pk=None):
    if site_pk is None:
        site_pk = Site.objects.get_current().pk
    return 'dbtemplates::%s::%s' % (slugify(name), site_pk)


def get_cache_notfound_key(name, site_pk=None):
    return get_cache_key(name, site_pk) + '::notfound'


def remove_notfound_key(instance):
    # Remove notfound key as soon as we save the template.
    cache.delete(get_cache_notfound_key(instance.name))


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
    remove_notfound_key(instance)
    cache.set(get_cache_key(instance.name), instance.content)


def invalidate_cache_for_sites(sender, instance, action, reverse,
                               model, pk_set, **kwargs):
    if action != 'post_add':
        return
    if isinstance(instance, Site):
        # model is dbtemplates.models.Template
        site = instance
        for template in model.objects.all():
            if template.pk in pk_set:
                cache.delete(get_cache_notfound_key(template.name, site.pk))
            else:
                cache.delete(get_cache_key(template.name, site.pk))
    else:
        # instance is of type dbtempaltes.models.Template
        # model is django.contrib.sites.models.Site
        template = instance
        for site in model.objects.all():
            if site.pk in pk_set:
                cache.delete(get_cache_notfound_key(template.name, site.pk))
            else:
                cache.delete(get_cache_key(template.name, site.pk))


def remove_cached_template(instance, **kwargs):
    """
    Called via Django's signals to remove cached templates, if the template
    in the database was changed or deleted.
    """
    cache.delete(get_cache_key(instance.name))
