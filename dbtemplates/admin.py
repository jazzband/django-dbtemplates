from django import forms
from django.contrib import admin
from django.db.models import get_app
from django.utils.translation import gettext_lazy as _
from django.core.exceptions import ImproperlyConfigured

from dbtemplates.models import Template

# Check if django-reversion is installed and use reversions' VersionAdmin
# as the base admin class if yes
try:
    get_app('reversion')
    from reversion.admin import VersionAdmin as TemplateModelAdmin
except ImproperlyConfigured:
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
        (_('Date information'), {
            'fields': (('creation_date', 'last_changed'),),
            'classes': ('collapse',),
        }),
    )
    list_display = ('name', 'creation_date', 'last_changed')
    list_filter = ('sites',)
    search_fields = ('name', 'content')

admin.site.register(Template, TemplateAdmin)
