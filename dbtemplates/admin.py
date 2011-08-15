import posixpath
from django import forms
from django.contrib import admin
from django.utils.translation import ungettext, ugettext_lazy as _
from django.utils.safestring import mark_safe

from dbtemplates.conf import settings
from dbtemplates.models import (Template,
    remove_cached_template, add_template_to_cache)
from dbtemplates.utils.template import check_template_syntax

# Check if django-reversion is installed and use reversions' VersionAdmin
# as the base admin class if yes
if settings.DBTEMPLATES_USE_REVERSION:
    from reversion.admin import VersionAdmin as TemplateModelAdmin
else:
    from django.contrib.admin import ModelAdmin as TemplateModelAdmin


class CodeMirrorTextArea(forms.Textarea):
    """
    A custom widget for the CodeMirror browser editor to be used with the
    content field of the Template model.
    """
    class Media:
        css = dict(screen=[posixpath.join(
            settings.DBTEMPLATES_MEDIA_PREFIX, 'css/editor.css')])
        js = [posixpath.join(settings.DBTEMPLATES_MEDIA_PREFIX, 'js/codemirror.js')]

    def render(self, name, value, attrs=None):
        result = []
        result.append(
            super(CodeMirrorTextArea, self).render(name, value, attrs))
        result.append(u"""
<script type="text/javascript">
  var editor = CodeMirror.fromTextArea('id_%(name)s', {
    path: "%(media_prefix)sjs/",
    parserfile: "parsedjango.js",
    stylesheet: "%(media_prefix)scss/django.css",
    continuousScanning: 500,
    height: "40.2em",
    tabMode: "shift",
    indentUnit: 4,
    lineNumbers: true
  });
</script>
""" % dict(media_prefix=settings.DBTEMPLATES_MEDIA_PREFIX, name=name))
        return mark_safe(u"".join(result))

if settings.DBTEMPLATES_USE_CODEMIRROR:
    TemplateContentTextArea = CodeMirrorTextArea
else:
    TemplateContentTextArea = forms.Textarea

if settings.DBTEMPLATES_AUTO_POPULATE_CONTENT:
    content_help_text = _("Leaving this empty causes Django to look for a "
        "template with the given name and populate this field with its "
        "content.")
else:
    content_help_text = ""


class TemplateAdminForm(forms.ModelForm):
    """
    Custom AdminForm to make the content textarea wider.
    """
    content = forms.CharField(
        widget=TemplateContentTextArea({'rows': '24'}),
        help_text=content_help_text, required=False)

    class Meta:
        model = Template


class TemplateAdmin(TemplateModelAdmin):
    form = TemplateAdminForm
    fieldsets = (
        (None, {
            'fields': ('name', 'content'),
            'classes': ('monospace',),
        }),
        (_('Advanced'), {
            'fields': (('sites'),),
        }),
        (_('Date/time'), {
            'fields': (('creation_date', 'last_changed'),),
            'classes': ('collapse',),
        }),
    )
    filter_horizontal = ('sites',)
    list_display = ('name', 'creation_date', 'last_changed', 'site_list')
    list_filter = ('sites',)
    save_as = True
    search_fields = ('name', 'content')
    actions = ['invalidate_cache', 'repopulate_cache', 'check_syntax']

    def invalidate_cache(self, request, queryset):
        for template in queryset:
            remove_cached_template(template)
        count = queryset.count()
        message = ungettext(
            "Cache of one template successfully invalidated.",
            "Cache of %(count)d templates successfully invalidated.",
            count)
        self.message_user(request, message % {'count': count})
    invalidate_cache.short_description = _("Invalidate cache of "
                                           "selected templates")

    def repopulate_cache(self, request, queryset):
        for template in queryset:
            add_template_to_cache(template)
        count = queryset.count()
        message = ungettext(
            "Cache successfully repopulated with one template.",
            "Cache successfully repopulated with %(count)d templates.",
            count)
        self.message_user(request, message % {'count': count})
    repopulate_cache.short_description = _("Repopulate cache with "
                                           "selected templates")

    def check_syntax(self, request, queryset):
        errors = []
        for template in queryset:
            valid, error = check_template_syntax(template)
            if not valid:
                errors.append('%s: %s' % (template.name, error))
        if errors:
            count = len(errors)
            message = ungettext(
                "Template syntax check FAILED for %(names)s.",
                "Template syntax check FAILED for %(count)d templates: %(names)s.",
                count)
            self.message_user(request, message %
                              {'count': count, 'names': ', '.join(errors)})
        else:
            count = queryset.count()
            message = ungettext(
                "Template syntax OK.",
                "Template syntax OK for %(count)d templates.", count)
            self.message_user(request, message % {'count': count})
    check_syntax.short_description = _("Check template syntax")

    def site_list(self, template):
        return ", ".join([site.name for site in template.sites.all()])
    site_list.short_description = _('sites')

admin.site.register(Template, TemplateAdmin)
