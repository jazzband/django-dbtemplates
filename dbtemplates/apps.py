from django.apps import AppConfig
from django.conf import settings
from django.db.models.signals import m2m_changed
from django.utils.translation import gettext_lazy as _


class DBTemplatesConfig(AppConfig):
    name = 'dbtemplates'
    verbose_name = _('Database templates')

    default_auto_field = 'django.db.models.AutoField'

    def ready(self):
        from .models import Template
        from .signal_handlers import verify_template_name_uniqueness_across_all_selected_sites

        if getattr(settings, 'DBTEMPLATES_UNIQUE', False):
            m2m_changed.connect(verify_template_name_uniqueness_across_all_selected_sites, sender=Template.sites.through)
