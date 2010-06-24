from django.conf import settings

CACHE_BACKEND = getattr(settings, 'DBTEMPLATES_CACHE_BACKEND', None)

ADD_DEFAULT_SITE = getattr(settings, 'DBTEMPLATES_ADD_DEFAULT_SITE', True)