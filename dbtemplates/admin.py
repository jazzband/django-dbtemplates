from django import forms
from django.conf import settings
from django.contrib import admin
from django.utils.translation import ungettext, ugettext_lazy as _

from dbtemplates.models import Template, backend, remove_cached_template, \
    add_template_to_cache

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
    if backend:
        actions = ['invalidate_cache', 'repopulate_cache']

    def invalidate_cache(self, request, queryset):
        if not backend:
            self.message_user(request, ("There is no active cache backend."))
            return
        for template in queryset:
            remove_cached_template(template)
        message = ungettext(
            "Cache of one template successfully invalidated.",
            "Cache of %(count)d templates successfully invalidated.",
            len(queryset))
        self.message_user(request, message % {'count': len(queryset)})
    invalidate_cache.short_description = _("Invalidate cache of selected templates")

    def repopulate_cache(self, request, queryset):
        if not backend:
            self.message_user(request, ("There is no active cache backend."))
            return
        for template in queryset:
            add_template_to_cache(template)
        message = ungettext(
            "Cache successfully repopulated with one template.",
            "Cache successfully repopulated with %(count)d templates.",
            len(queryset))
        self.message_user(request, message % {'count': len(queryset)})
    repopulate_cache.short_description = _("Repopulate cache with selected templates")

    def site_list(self, template):
          return ", ".join([site.name for site in template.sites.all()])
    site_list.short_description = _('sites')

admin.site.register(Template, TemplateAdmin)
