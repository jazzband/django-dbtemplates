from pkg_resources import get_distribution, DistributionNotFound

try:
    __version__ = get_distribution("django-dbtemplates").version
except DistributionNotFound:
    # package is not installed
    __version__ = None


default_app_config = 'dbtemplates.apps.DBTemplatesConfig'
