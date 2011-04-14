import posixpath
from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

if "dbtemplates" in getattr(settings, "CACHES", {}):
    # If we are on Django 1.3 AND using the new CACHES setting..
    cache = "dbtemplates"
else:
    # ..or fall back to the old CACHE_BACKEND setting
    cache = getattr(settings, "DBTEMPLATES_CACHE_BACKEND", None)
if not cache:
    raise ImproperlyConfigured("Please specify a dbtemplates "
                               "cache backend in your settings.")
elif isinstance(cache, basestring) and cache.startswith("dbtemplates."):
    raise ImproperlyConfigured("Please upgrade to one of the supported "
                               "backends as defined in the Django docs.")
CACHE_BACKEND = cache

ADD_DEFAULT_SITE = getattr(settings, 'DBTEMPLATES_ADD_DEFAULT_SITE', True)

AUTO_POPULATE_CONTENT = getattr(
    settings, 'DBTEMPLATES_AUTO_POPULATE_CONTENT', True)

base_url = getattr(settings, "STATIC_URL", None)
if base_url is None:
    base_url = settings.MEDIA_URL
MEDIA_PREFIX = getattr(settings, 'DBTEMPLATES_MEDIA_PREFIX',
                       posixpath.join(base_url, "dbtemplates/"))

USE_REVERSION = getattr(settings, 'DBTEMPLATES_USE_REVERSION', False)

if USE_REVERSION and 'reversion'not in settings.INSTALLED_APPS:
    raise ImproperlyConfigured("Please add reversion to your "
        "INSTALLED_APPS setting to make use of it in dbtemplates.")

USE_CODEMIRROR = getattr(settings, 'DBTEMPLATES_USE_CODEMIRROR', False)
