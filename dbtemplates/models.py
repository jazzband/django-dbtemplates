from dbtemplates.conf import settings
from dbtemplates.utils.cache import (
    add_template_to_cache,
    remove_cached_template,
)
from dbtemplates.utils.template import get_template_source

from django.contrib.sites.managers import CurrentSiteManager
from django.contrib.sites.models import Site
from django.db import models
from django.db.models import signals
from django.template import TemplateDoesNotExist
from django.utils.translation import gettext_lazy as _


class Template(models.Model):
    """
    Defines a template model for use with the database template loader.
    The field ``name`` is the equivalent to the filename of a static template.
    """
    id = models.AutoField(primary_key=True, verbose_name=_('ID'),
                          serialize=False, auto_created=True)
    name = models.CharField(_('name'), max_length=100,
                            help_text=_("Example: 'flatpages/default.html'"))
    content = models.TextField(_('content'), blank=True)
    sites = models.ManyToManyField(Site, verbose_name=_('sites'),
                                   blank=True)
    creation_date = models.DateTimeField(_('creation date'), auto_now_add=True)
    last_changed = models.DateTimeField(_('last changed'), auto_now=True)

    objects = models.Manager()
    on_site = CurrentSiteManager('sites')

    class Meta:
        db_table = 'django_template'
        verbose_name = _('template')
        verbose_name_plural = _('templates')
        ordering = ('name',)

    def __str__(self):
        return self.name

    def populate(self, name=None):
        """
        Tries to find a template with the same name and populates
        the content field if found.
        """
        if name is None:
            name = self.name
        try:
            source = get_template_source(name)
        except TemplateDoesNotExist:
            pass
        else:
            self.content = source


def add_default_site(instance, **kwargs):
    """
    Called via Django's signals to cache the templates, if the template
    in the database was added or changed, only if
    DBTEMPLATES_ADD_DEFAULT_SITE setting is set.
    """
    instance.sites.add(Site.objects.get_current())


def populate_empty_content(instance, **kwargs):
    # If content is empty look for a template with the given name and
    # populate the template instance with its content.
    if not instance.content:
        instance.populate()


if settings.DBTEMPLATES_ADD_DEFAULT_SITE:
    signals.post_save.connect(add_default_site, sender=Template)

if settings.DBTEMPLATES_AUTO_POPULATE_CONTENT:
    signals.pre_save.connect(populate_empty_content, sender=Template)

signals.post_save.connect(add_template_to_cache, sender=Template)
signals.pre_delete.connect(remove_cached_template, sender=Template)
