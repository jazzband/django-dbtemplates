import os
import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from django.conf import settings as django_settings
from django.core.cache.backends.base import BaseCache
from django.core.management import call_command
from django.db.models.signals import post_save
from django.template import loader, TemplateDoesNotExist
from django.test import TestCase, modify_settings, override_settings
from django.test.signals import receiver, setting_changed

from django.contrib.sites.models import Site

from dbtemplates.conf import settings
from dbtemplates.models import Template, add_default_site
from dbtemplates.utils.cache import get_cache_backend, get_cache_key
from dbtemplates.utils.template import (get_template_source,
                                        check_template_syntax)
from dbtemplates.management.commands.sync_templates import (FILES_TO_DATABASE,
                                                            DATABASE_TO_FILES)


@receiver(setting_changed)
def handle_add_default_site(sender, setting, value, **kwargs):
    if setting == "DBTEMPLATES_ADD_DEFAULT_SITE":
        if value:
            post_save.connect(add_default_site, sender=Template)
        else:
            post_save.disconnect(add_default_site, sender=Template)


@contextmanager
def temptemplate(name: str, cleanup: bool = True):
    temp_template_dir = Path(tempfile.mkdtemp('dbtemplates'))
    temp_template_path = temp_template_dir / name
    try:
        yield temp_template_path
    finally:
        shutil.rmtree(temp_template_dir)


class DbTemplatesTestCase(TestCase):
    @modify_settings(
        TEMPLATES={
            "append": "dbtemplates.loader.Loader",
        },
    )
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

    def test_basics(self):
        self.assertQuerySetEqual(self.t1.sites.all(), Site.objects.filter(id=self.site1.id))
        self.assertIn("base", self.t1.content)
        self.assertQuerySetEqual(Template.objects.filter(sites=self.site1),
                                 Template.objects.filter(id__in=[self.t1.id, self.t2.id]))
        self.assertQuerySetEqual(self.t2.sites.all(), Site.objects.filter(id__in=[self.site1.id, self.site2.id]))

    @override_settings(DBTEMPLATES_ADD_DEFAULT_SITE=False)
    def test_empty_sites(self):
        self.t3 = Template.objects.create(
            name='footer.html', content='footer')
        self.assertQuerySetEqual(self.t3.sites.all(), self.t3.sites.none())

    @override_settings(DBTEMPLATES_ADD_DEFAULT_SITE=False)
    def test_load_templates_sites(self):
        t_site1 = Template.objects.create(
            name='copyright.html', content='(c) example.com')
        t_site1.sites.add(self.site1)
        t_site2 = Template.objects.create(
            name='copyright.html', content='(c) example.org')
        t_site2.sites.add(self.site2)

        new_site = Site.objects.create(
            domain="example.net", name="example.net")
        with self.settings(SITE_ID=new_site.id):
            Site.objects.clear_cache()

            self.assertRaises(TemplateDoesNotExist,
                              loader.get_template, "copyright.html")

    def test_load_templates(self):
        result = loader.get_template("base.html").render()
        self.assertEqual(result, 'base')
        result2 = loader.get_template("sub.html").render()
        self.assertEqual(result2, 'sub')

    def test_error_templates_creation(self):
        call_command('create_error_templates', force=True, verbosity=0)
        self.assertQuerySetEqual(Template.objects.filter(sites=self.site1),
                                 Template.objects.filter())
        self.assertTrue(Template.objects.filter(name='404.html').exists())

    def test_automatic_sync(self):
        admin_base_template = get_template_source('admin/base.html')
        template = Template.objects.create(name='admin/base.html')
        self.assertEqual(admin_base_template, template.content)

    def test_sync_templates(self):
        old_template_dirs = settings.TEMPLATES[0].get('DIRS', [])
        with temptemplate('temp_test.html') as temp_template_path:
            with open(temp_template_path, 'w', encoding='utf-8') as temp_template:
                temp_template.write('temp test')
            try:
                settings.TEMPLATES[0]['DIRS'] = (temp_template_path.parent,)
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
                t.content = 'temp test modified'
                t.save()
                call_command('sync_templates', force=True,
                             verbosity=0, overwrite=DATABASE_TO_FILES)
                with open(temp_template_path, encoding='utf-8') as f:
                    self.assertEqual('temp test modified', f.read())

                call_command('sync_templates', force=True, verbosity=0,
                             delete=True, overwrite=DATABASE_TO_FILES)
                self.assertTrue(os.path.exists(temp_template_path))
                self.assertFalse(
                    Template.objects.filter(name='temp_test.html').exists())
            finally:
                settings.TEMPLATES[0]['DIRS'] = old_template_dirs

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

    def test_cache_invalidation(self):
        # Add t1 into the cache of site2
        self.t1.sites.add(self.site2)
        with mock.patch('django.contrib.sites.models.SiteManager.get_current',
                        return_value=self.site2):
            result = loader.get_template("base.html").render()
            self.assertEqual(result, 'base')

        # Update content
        self.t1.content = 'new content'
        self.t1.save()
        result = loader.get_template("base.html").render()
        self.assertEqual(result, 'new content')

        # Cache invalidation should work across sites.
        # Site2 should see the new content.
        with mock.patch('django.contrib.sites.models.SiteManager.get_current',
                        return_value=self.site2):
            result = loader.get_template("base.html").render()
            self.assertEqual(result, 'new content')
