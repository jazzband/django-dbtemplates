# -*- coding: utf-8 -*-
from datetime import datetime
from django.db import models
from django.conf import settings
from django.db.models import signals
from django.contrib.sites.models import Site
from django.utils.translation import gettext_lazy as _
from django.template import TemplateDoesNotExist
from django.template.loader import find_template_source
from django.core.exceptions import ImproperlyConfigured

class Template(models.Model):
    """
    Defines a template model for use with the database template loader.
    The field ``name`` is the equivalent to the filename of a static template.
    """
    name = models.CharField(_('name'), unique=True, max_length=100, help_text=_("Example: 'flatpages/default.html'"))
    content = models.TextField(_('content'), blank=True)
    sites = models.ManyToManyField(Site, default=[settings.SITE_ID])
    creation_date = models.DateTimeField(_('creation date'), default=datetime.now)
    last_changed = models.DateTimeField(_('last changed'), default=datetime.now)

    class Meta:
        db_table = 'django_template'
        verbose_name = _('template')
        verbose_name_plural = _('templates')
        ordering = ('name',)

    def __unicode__(self):
        return self.name
    
    def save(self, *args, **kwargs):
        self.last_changed = datetime.now()
        # If content is empty look for a template with the given name and
        # populate the template instance with its content.
        if not self.content:
            try:
                source, origin = find_template_source(self.name)
                if source:
                    self.content = source
            except TemplateDoesNotExist:
                pass
        super(Template, self).save(*args, **kwargs)

def get_cache_backend():
    path = getattr(settings, 'DBTEMPLATES_CACHE_BACKEND', False)
    if path:
        i = path.rfind('.')
        module, attr = path[:i], path[i+1:]
        try:
            mod = __import__(module, {}, {}, [attr])
        except ImportError, e:
            raise ImproperlyConfigured, 'Error importing dbtemplates cache backend %s: "%s"' % (module, e)
        try:
            cls = getattr(mod, attr)
        except AttributeError:
            raise ImproperlyConfigured, 'Module "%s" does not define a "%s" cache backend' % (module, attr)
        return cls()
    return False

backend = get_cache_backend()

def add_template_to_cache(instance, **kwargs):
    """
    Called via Django's signals to cache the templates, if the template
    in the database was added or changed.
    """
    backend.save(instance.name, instance.content)

def remove_cached_template(instance, **kwargs):
    """
    Called via Django's signals to remove cached templates, if the template
    in the database was changed or deleted.
    """
    backend.remove(instance.name)

if backend:
    signals.post_save.connect(remove_cached_template, sender=Template)
    signals.post_save.connect(add_template_to_cache, sender=Template)
    signals.pre_delete.connect(remove_cached_template, sender=Template)

__test__ = {'API_TESTS':"""
>>> from django.template import loader, Context
>>> test_site = Site.objects.get(pk=1)
>>> test_site
<Site: example.com>
>>> t1 = Template(name='base.html', content="<html><head></head><body>{% block content %}Welcome at {{ title }}{% endblock %}</body></html>")
>>> t1.save()
>>> t1.sites.add(test_site)
>>> t1
<Template: base.html>
>>> t2 = Template(name='sub.html', content='{% extends "base.html" %}{% block content %}This is {{ title }}{% endblock %}')
>>> t2.save()
>>> t2.sites.add(test_site)
>>> t2
<Template: sub.html>
>>> Template.objects.filter(sites=test_site)
[<Template: 404.html>, <Template: 500.html>, <Template: base.html>, <Template: sub.html>]
>>> t2.sites.all()
[<Site: example.com>]
>>> from dbtemplates.loader import load_template_source
>>> loader.template_source_loaders = [load_template_source]
>>> loader.get_template("base.html").render(Context({'title':'MainPage'}))
u'<html><head></head><body>Welcome at MainPage</body></html>'
>>> loader.get_template("sub.html").render(Context({'title':'SubPage'}))
u'<html><head></head><body>This is SubPage</body></html>'
"""}
