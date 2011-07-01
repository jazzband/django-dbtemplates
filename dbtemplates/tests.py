from __future__ import with_statement

from django.core.management import call_command
from django.template import loader, Context
from django.test import TestCase

from django.contrib.sites.models import Site

from dbtemplates.conf import settings
from dbtemplates.models import Template
from dbtemplates.utils.template import get_template_source


class DbTemplatesTestCase(TestCase):
    def setUp(self):
        self.site1, created1 = Site.objects.get_or_create(
            domain="example.com", name="example.com")
        self.site2, created2 = Site.objects.get_or_create(
            domain="example.org", name="example.org")
        self.t1, _ = Template.objects.get_or_create(
            name='base.html', content='base')
        self.t2, _ = Template.objects.get_or_create(
            name='sub.html', content='sub')
        self.t2.sites.add(self.site2)

    def test_basiscs(self):
        self.assertEqual(list(self.t1.sites.all()), [self.site1])
        self.assertTrue("base" in self.t1.content)
        self.assertEqual(list(Template.objects.filter(sites=self.site1)),
                         [self.t1, self.t2])
        self.assertEqual(list(self.t2.sites.all()), [self.site1, self.site2])

    def test_empty_sites(self):
        old_add_default_site = settings.DBTEMPLATES_ADD_DEFAULT_SITE
        try:
            settings.DBTEMPLATES_ADD_DEFAULT_SITE = False
            self.t3 = Template.objects.create(
                name='footer.html', content='footer')
            self.assertEqual(list(self.t3.sites.all()), [])
        finally:
            settings.DBTEMPLATES_ADD_DEFAULT_SITE = old_add_default_site

    def test_load_templates(self):
        result = loader.get_template("base.html").render(Context({}))
        self.assertEqual(result, 'base')
        result2 = loader.get_template("sub.html").render(Context({}))
        self.assertEqual(result2, 'sub')

    def test_error_templates_creation(self):
        call_command('create_error_templates', force=True, verbosity=0)
        self.assertEqual(list(Template.objects.filter(sites=self.site1)),
                         list(Template.objects.filter()))

    def test_automatic_sync(self):
        admin_base_template = get_template_source('admin/base.html')
        template = Template.objects.create(name='admin/base.html')
        self.assertEqual(admin_base_template, template.content)
