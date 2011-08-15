from __future__ import with_statement
import codecs
import os
import shutil
import tempfile

from django.core.cache.backends.base import BaseCache
from django.core.management import call_command
from django.template import loader, Context
from django.test import TestCase

from django.contrib.sites.models import Site

from dbtemplates.conf import settings
from dbtemplates.models import Template
from dbtemplates.utils.cache import get_cache_backend
from dbtemplates.utils.template import (get_template_source,
                                        check_template_syntax)
from dbtemplates.management.commands.sync_templates import (FILES_TO_DATABASE,
                                                            DATABASE_TO_FILES)

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
        self.assertTrue(Template.objects.filter(name='404.html').exists())

    def test_automatic_sync(self):
        admin_base_template = get_template_source('admin/base.html')
        template = Template.objects.create(name='admin/base.html')
        self.assertEqual(admin_base_template, template.content)

    def test_sync_templates(self):
        old_template_dirs = settings.TEMPLATE_DIRS
        temp_template_dir = tempfile.mkdtemp('dbtemplates')
        last_path_part = temp_template_dir.split('/')[-1]
        temp_template_path = os.path.join(temp_template_dir, 'temp_test.html')
        temp_template = codecs.open(temp_template_path, 'w')
        try:
            temp_template.write('temp test')
            settings.TEMPLATE_DIRS = (temp_template_dir,)
            self.assertFalse(Template.objects.filter(name='temp_test.html').exists())
            call_command('sync_templates',
                force=True, verbosity=0, overwrite=FILES_TO_DATABASE)
            self.assertTrue(Template.objects.filter(name='temp_test.html').exists())

            t = Template.objects.get(name='temp_test.html')
            t.content = 'temp test modified'
            t.save()
            call_command('sync_templates',
                force=True, verbosity=0, overwrite=DATABASE_TO_FILES)
            self.assertTrue('modified' in codecs.open(temp_template_path).read())

            call_command('sync_templates',
                force=True, verbosity=0, delete=True, overwrite=DATABASE_TO_FILES)
            self.assertTrue(os.path.exists(temp_template_path))
            self.assertFalse(Template.objects.filter(name='temp_test.html').exists())
        finally:
            temp_template.close()
            settings.TEMPLATE_DIRS = old_template_dirs
            shutil.rmtree(temp_template_dir)

    def test_get_cache(self):
        self.assertTrue(isinstance(get_cache_backend(), BaseCache))

    def test_check_template_syntax(self):
        bad_template, _ = Template.objects.get_or_create(
            name='bad.html', content='{% if foo %}Bar')
        good_template, _ = Template.objects.get_or_create(
            name='good.html', content='{% if foo %}Bar{% endif %}')
        self.assertFalse(check_template_syntax(bad_template)[0])
        self.assertTrue(check_template_syntax(good_template)[0])
