from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class DBTemplatesConfig(AppConfig):
    name = 'dbtemplates'
    verbose_name = _('Database templates')
