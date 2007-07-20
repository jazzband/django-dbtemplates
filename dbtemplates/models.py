# -*- coding: utf-8 -*-
from django.db import models
from django.template import loader, Context
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

__test__ = {'API_TESTS':"""
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
[<Template: base.html>, <Template: sub.html>]
>>> t2.sites.all()
[<Site: example.com>]
>>> from dbtemplates.loader import load_template_source
>>> loader.template_source_loaders = [load_template_source]
>>> loader.get_template("base.html").render(Context({'title':'MainPage'}))
'<html><head></head><body>Welcome at MainPage</body></html>'
>>> loader.get_template("sub.html").render(Context({'title':'SubPage'}))
'<html><head></head><body>This is SubPage</body></html>'
"""}