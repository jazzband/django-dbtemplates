from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


class DBTemplatesConfig(AppConfig):
    name = "dbtemplates"
    verbose_name = _("Database templates")
    default_auto_field = "django.db.models.AutoField"
