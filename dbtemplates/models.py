# -*- coding: utf-8 -*-
from datetime import datetime

from django.db import models
from django.db.models import signals
from django.template import TemplateDoesNotExist
from django.utils.translation import gettext_lazy as _

from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager

from dbtemplates import settings
from dbtemplates.utils import (add_default_site, add_template_to_cache,
    remove_cached_template, get_template_source)


class Template(models.Model):
    """
    Defines a template model for use with the database template loader.
    The field ``name`` is the equivalent to the filename of a static template.
    """
    name = models.CharField(_('name'), unique=True, max_length=100,
                            help_text=_("Example: 'flatpages/default.html'"))
    content = models.TextField(_('content'), blank=True)
    sites = models.ManyToManyField(Site, verbose_name=_('sites'))
    creation_date = models.DateTimeField(_('creation date'),
                                         default=datetime.now)
    last_changed = models.DateTimeField(_('last changed'),
                                        default=datetime.now)

    objects = models.Manager()
    on_site = CurrentSiteManager('sites')

    class Meta:
        db_table = 'django_template'
        verbose_name = _('template')
        verbose_name_plural = _('templates')
        ordering = ('name',)

    def __unicode__(self):
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
            if source:
                self.content = source
        except TemplateDoesNotExist:
            pass

    def save(self, *args, **kwargs):
        self.last_changed = datetime.now()
        # If content is empty look for a template with the given name and
        # populate the template instance with its content.
        if settings.AUTO_POPULATE_CONTENT and not self.content:
            self.populate()
        super(Template, self).save(*args, **kwargs)


signals.post_save.connect(add_default_site, sender=Template)
signals.post_save.connect(add_template_to_cache, sender=Template)
signals.pre_delete.connect(remove_cached_template, sender=Template)
