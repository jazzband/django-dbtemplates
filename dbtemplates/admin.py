from django import forms
from django.conf import settings
from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from dbtemplates.models import Template

# Check if django-reversion is installed and use reversions' VersionAdmin
# as the base admin class if yes
if 'reversion'in settings.INSTALLED_APPS:
    from reversion.admin import VersionAdmin as TemplateModelAdmin
else:
    from django.contrib.admin import ModelAdmin as TemplateModelAdmin

class TemplateAdminForm(forms.ModelForm):
    """
    Custom AdminForm to make the content textarea wider.
    """
    content = forms.CharField(
        widget=forms.Textarea({'cols': '80', 'rows': '24'}),
        help_text=_("Leaving this empty causes Django to look for a template "
            "with the given name and populate this field with its content."),
        required=False)

    class Meta:
        model = Template

class TemplateAdmin(TemplateModelAdmin):
    form = TemplateAdminForm
    fieldsets = (
        (None, {
            'fields': ('name', 'content', 'sites'),
            'classes': ('monospace',),
        }),
        (_('Date/time'), {
            'fields': (('creation_date', 'last_changed'),),
            'classes': ('collapse',),
        }),
    )
    list_display = ('name', 'creation_date', 'last_changed', 'site_list')
    list_filter = ('sites',)
    search_fields = ('name', 'content')

    def site_list(self, template):
          return ", ".join([site.name for site in template.sites.all()])
    site_list.short_description = _('sites')

admin.site.register(Template, TemplateAdmin)
