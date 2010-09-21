# -*- coding: utf-8 -*-
from datetime import datetime

from django import VERSION
from django.db import models
from django.db.models import signals
from django.utils.translation import gettext_lazy as _
from django.template import TemplateDoesNotExist
from django.core.exceptions import ImproperlyConfigured

from django.contrib.sites.models import Site
from django.contrib.sites.managers import CurrentSiteManager

from dbtemplates import settings

print VERSION, VERSION[:2] < (1, 2)
if VERSION[:2] >= (1, 2):
    from django.template.loader import find_template
else:
    from django.template.loader import find_template_source  as find_template

class Template(models.Model):
    """
    Defines a template model for use with the database template loader.
    The field ``name`` is the equivalent to the filename of a static template.
    """
    name = models.CharField(_('name'), unique=True, max_length=100,
                            help_text=_("Example: 'flatpages/default.html'"))
    content = models.TextField(_('content'), blank=True)
    sites = models.ManyToManyField(Site)
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
            source, origin = find_template(name)
            if source:
                self.content = source
        except TemplateDoesNotExist:
            pass

    def save(self, *args, **kwargs):
        self.last_changed = datetime.now()
        # If content is empty look for a template with the given name and
        # populate the template instance with its content.
        if not self.content:
            self.populate()
        super(Template, self).save(*args, **kwargs)

def get_cache_backend():
    path = settings.CACHE_BACKEND
    if path:
        i = path.rfind('.')
        module, attr = path[:i], path[i+1:]
        try:
            mod = __import__(module, {}, {}, [attr])
        except ImportError, e:
            raise ImproperlyConfigured(
                'Error importing dbtemplates cache backend %s: "%s"' %
                (module, e))
        try:
            cls = getattr(mod, attr)
        except AttributeError:
            raise ImproperlyConfigured(
                'Module "%s" does not define a "%s" cache backend' %
                (module, attr))
        return cls()
    return False

backend = get_cache_backend()

def add_default_site(instance, **kwargs):
    """
    Called via Django's signals to cache the templates, if the template
    in the database was added or changed, only if DBTEMPLATES_ADD_DEFAULT_SITE
    setting is set.
    """
    if settings.ADD_DEFAULT_SITE:
        current_site = Site.objects.get_current()
        if current_site not in instance.sites.all():
            instance.sites.add(current_site)

signals.post_save.connect(add_default_site, sender=Template)

def add_template_to_cache(instance, **kwargs):
    """
    Called via Django's signals to cache the templates, if the template
    in the database was added or changed.
    """
    remove_cached_template(instance)
    backend.save(instance.name, instance.content)

def remove_cached_template(instance, **kwargs):
    """
    Called via Django's signals to remove cached templates, if the template
    in the database was changed or deleted.
    """
    backend.remove(instance.name)

if backend:
    signals.post_save.connect(add_template_to_cache, sender=Template)
    signals.pre_delete.connect(remove_cached_template, sender=Template)
