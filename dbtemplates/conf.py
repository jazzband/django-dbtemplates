import posixpath

from django.core.exceptions import ImproperlyConfigured
from django.conf import settings

from appconf import AppConf


class DbTemplatesConf(AppConf):
    USE_CODEMIRROR = False
    USE_REVERSION = False
    ADD_DEFAULT_SITE = True
    AUTO_POPULATE_CONTENT = True
    MEDIA_PREFIX = None
    CACHE_BACKEND = None

    def configure_media_prefix(self, value):
        if value is None:
            base_url = getattr(settings, "STATIC_URL", None)
            if base_url is None:
                base_url = settings.MEDIA_URL
            value = posixpath.join(base_url, "dbtemplates/")
        return value

    def configure_cache_backend(self, value):
        # If we are on Django 1.3 AND using the new CACHES setting..
        if hasattr(settings, "CACHES"):
            if "dbtemplates" in settings.CACHES:
                return "dbtemplates"
            else:
                return "default"
        if isinstance(value, basestring) and value.startswith("dbtemplates."):
            raise ImproperlyConfigured("Please upgrade to one of the "
                                       "supported backends as defined "
                                       "in the Django docs.")
        return value

    def configure_use_reversion(self, value):
        if value and 'reversion' not in settings.INSTALLED_APPS:
            raise ImproperlyConfigured("Please add 'reversion' to your "
                "INSTALLED_APPS setting to make use of it in dbtemplates.")
        return value
