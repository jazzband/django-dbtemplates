from django.apps import AppConfig
try:
    #Django 3 and bellow
    from django.utils.translation import ugettext_lazy as _
except ImportError:
    #Django 4+
    from django.utils.translation import gettext_lazy as _


class DBTemplatesConfig(AppConfig):
    name = 'dbtemplates'
    verbose_name = _('Database templates')
