import io
import os
import shutil
import tempfile

from django.conf import settings as django_settings
from django.core.cache.backends.base import BaseCache
from django.core.management import call_command
from django.template import loader, TemplateDoesNotExist
from django.test import TestCase

from django.contrib.sites.models import Site

from dbtemplates.conf import settings
from dbtemplates.models import Template
from dbtemplates.utils.cache import get_cache_backend, get_cache_key
from dbtemplates.utils.template import (get_template_source,
                                        check_template_syntax)
from dbtemplates.management.commands.sync_templates import (FILES_TO_DATABASE,
                                                            DATABASE_TO_FILES)


class DbTemplatesTestCase(TestCase):
    def setUp(self):
        self.old_TEMPLATES = settings.TEMPLATES
        if 'dbtemplates.loader.Loader' not in settings.TEMPLATES:
            loader.template_source_loaders = None
            settings.TEMPLATES = list(settings.TEMPLATES) + [
                'dbtemplates.loader.Loader'
            ]

        self.site1, created1 = Site.objects.get_or_create(
            domain="example.com", name="example.com")
        self.site2, created2 = Site.objects.get_or_create(
            domain="example.org", name="example.org")
        self.t1, _ = Template.objects.get_or_create(
            name='base.html', content='base')
        self.t2, _ = Template.objects.get_or_create(
            name='sub.html', content='sub')
        self.t2.sites.add(self.site2)

    def tearDown(self):
        loader.template_source_loaders = None
        settings.TEMPLATES = self.old_TEMPLATES

    def test_basics(self):
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

    def test_load_templates_sites(self):
        old_add_default_site = settings.DBTEMPLATES_ADD_DEFAULT_SITE
        old_site_id = django_settings.SITE_ID
        try:
            settings.DBTEMPLATES_ADD_DEFAULT_SITE = False
            t_site1 = Template.objects.create(
                name='copyright.html', content='(c) example.com')
            t_site1.sites.add(self.site1)
            t_site2 = Template.objects.create(
                name='copyright.html', content='(c) example.org')
            t_site2.sites.add(self.site2)

            django_settings.SITE_ID = Site.objects.create(
                domain="example.net", name="example.net").id
            Site.objects.clear_cache()

            self.assertRaises(TemplateDoesNotExist,
                              loader.get_template, "copyright.html")
        finally:
            django_settings.SITE_ID = old_site_id
            settings.DBTEMPLATES_ADD_DEFAULT_SITE = old_add_default_site

    def test_load_templates(self):
        result = loader.get_template("base.html").render()
        self.assertEqual(result, 'base')
        result2 = loader.get_template("sub.html").render()
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
        old_template_dirs = settings.TEMPLATES[0].get('DIRS', [])
        temp_template_dir = tempfile.mkdtemp('dbtemplates')
        temp_template_path = os.path.join(temp_template_dir, 'temp_test.html')
        temp_template = io.open(temp_template_path, 'w', encoding='utf-8')
        try:
            temp_template.write(u'temp test')
            settings.TEMPLATES[0]['DIRS'] = (temp_template_dir,)
            # these works well if is not settings patched at runtime
            # for supporting django < 1.7 tests we must patch dirs in runtime
            from dbtemplates.management.commands import sync_templates
            sync_templates.DIRS = settings.TEMPLATES[0]['DIRS']

            self.assertFalse(
                Template.objects.filter(name='temp_test.html').exists())
            call_command('sync_templates', force=True,
                         verbosity=0, overwrite=FILES_TO_DATABASE)
            self.assertTrue(
                Template.objects.filter(name='temp_test.html').exists())

            t = Template.objects.get(name='temp_test.html')
            t.content = u'temp test modified'
            t.save()
            call_command('sync_templates', force=True,
                         verbosity=0, overwrite=DATABASE_TO_FILES)
            self.assertEqual(u'temp test modified',
                             io.open(temp_template_path,
                                     encoding='utf-8').read())

            call_command('sync_templates', force=True, verbosity=0,
                         delete=True, overwrite=DATABASE_TO_FILES)
            self.assertTrue(os.path.exists(temp_template_path))
            self.assertFalse(
                Template.objects.filter(name='temp_test.html').exists())
        finally:
            temp_template.close()
            settings.TEMPLATES[0]['DIRS'] = old_template_dirs
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

    def test_get_cache_name(self):
        self.assertEqual(get_cache_key('name with spaces'),
                         'dbtemplates::name-with-spaces::1')
