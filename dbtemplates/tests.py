from django import VERSION
from django.core.management import call_command
from django.template import loader, Context
from django.test import TestCase

from django.contrib.sites.models import Site

from dbtemplates import settings
from dbtemplates.loader import load_template_source
from dbtemplates.models import Template, get_template_source

class DbTemplatesTestCase(TestCase):
    def setUp(self):
        self.site1, created1 = Site.objects.get_or_create(domain="example.com", name="example.com")
        self.site2, created2 = Site.objects.get_or_create(domain="example.org", name="example.org")

    def test_basiscs(self):
        t1 = Template(name='base.html', content='<html><head></head><body>{% block content %}Welcome at {{ title }}{% endblock %}</body></html>')
        t1.save()
        self.assertEqual(Site.objects.get_current(), t1.sites.all()[0])
        self.assertTrue("Welcome at" in t1.content)

        t2 = Template(name='sub.html', content='{% extends "base.html" %}{% block content %}This is {{ title }}{% endblock %}')
        t2.save()
        t2.sites.add(self.site2)

        self.assertEqual(list(Template.objects.filter(sites=self.site1)), [t1, t2])
        self.assertEqual(list(t2.sites.all()), [self.site1, self.site2])

    def test_load_templates(self):
        self.test_basiscs()
        original_template_source_loaders = loader.template_source_loaders
        loader.template_source_loaders = [load_template_source]
        try:
            result1 = loader.get_template("base.html").render(Context({'title':'MainPage'}))
            self.assertEqual(result1, u'<html><head></head><body>Welcome at MainPage</body></html>')
            result2 = loader.get_template("sub.html").render(Context({'title':'SubPage'}))
            self.assertEqual(result2, u'<html><head></head><body>This is SubPage</body></html>')

            if VERSION[:2] >= (1, 2):
                from dbtemplates.loader import Loader
                dbloader = Loader()
                loader.template_source_loaders = [dbloader.load_template_source]
                result = loader.get_template("base.html").render(Context({'title':'MainPage'}))
                self.assertEqual(result, u'<html><head></head><body>Welcome at MainPage</body></html>')
                result2 = loader.get_template("sub.html").render(Context({'title':'SubPage'}))
                self.assertEqual(result2, u'<html><head></head><body>This is SubPage</body></html>')
        finally:
            loader.template_source_loaders = original_template_source_loaders

    def test_error_templates_creation(self):
        call_command('create_error_templates', force=True, verbosity=0)
        self.assertEqual(list(Template.objects.filter(sites=self.site1)),
            list(Template.objects.filter()))

    def test_disabling_default_site(self):
        old_add_default_site = settings.ADD_DEFAULT_SITE
        settings.ADD_DEFAULT_SITE = False
        t3 = Template.objects.create(name='footer.html', content='ohai')
        self.assertEqual(list(t3.sites.all()), [])
        settings.ADD_DEFAULT_SITE = old_add_default_site

    def test_automatic_sync(self):
        admin_base_template = get_template_source('admin/base.html')
        template = Template.objects.create(name='admin/base.html')
        self.assertEqual(admin_base_template, template.content)
