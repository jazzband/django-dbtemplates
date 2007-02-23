from django.db import models
from django.core import validators
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _

class Template(models.Model):
    """
    Defines a template model for use with the database template loader.
    The field ``name`` is the equivalent to the filename of a static template.
    """
    name = models.CharField(_('name'), unique=True, maxlength=100, help_text=_("Example: 'flatpages/default.html'"))
    content = models.TextField(_('content'))
    sites = models.ManyToManyField(Site)
    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    last_changed = models.DateTimeField(_('last changed'), auto_now=True)
    class Meta:
        db_table = 'django_template'
        verbose_name = _('template')
        verbose_name_plural = _('templates')
        ordering = ('name',)
    class Admin:
        fields = ((None, {'fields': ('name', 'content', 'sites')}),)
        list_display = ('name', 'creation_date', 'last_changed')
        list_filter = ('sites',)
        search_fields = ('name','content')

    def __str__(self):
        return self.name