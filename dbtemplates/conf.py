import posixpath

from django.core.exceptions import ImproperlyConfigured

from dbtemplates.utils.settings import AppSettings


class DbTemplatesSettings(AppSettings):
    USE_CODEMIRROR = False
    USE_REVERSION = False
    ADD_DEFAULT_SITE = True
    AUTO_POPULATE_CONTENT = True
    MEDIA_PREFIX = None
    CACHE_BACKEND = None

    def configure_media_prefix(self, value):
        if value is None:
            base_url = getattr(self, "STATIC_URL", None)
            if base_url is None:
                base_url = self.MEDIA_URL
            value = posixpath.join(base_url, "dbtemplates/")
        return value

    def configure_cache_backend(self, value):
        # If we are on Django 1.3 AND using the new CACHES setting..
        if hasattr(self, "CACHES"):
            if "dbtemplates" in self.CACHES:
                return "dbtemplates"
            else:
                return "default"
        if isinstance(value, basestring) and value.startswith("dbtemplates."):
            raise ImproperlyConfigured("Please upgrade to one of the "
                                       "supported backends as defined "
                                       "in the Django docs.")
        return value

    def configure_use_reversion(self, value):
        if value and 'reversion' not in self.INSTALLED_APPS:
            raise ImproperlyConfigured("Please add 'reversion' to your "
                "INSTALLED_APPS setting to make use of it in dbtemplates.")
        return value

settings = DbTemplatesSettings("DBTEMPLATES")
