import shutil
import tempfile
from contextlib import contextmanager
from pathlib import Path
from unittest import mock

from django.core.cache.backends.base import BaseCache
from django.core.management import call_command
from django.db.models.signals import post_save
from django.template import loader, TemplateDoesNotExist
from django.test import TestCase, modify_settings, override_settings
from django.test.signals import receiver, setting_changed

from django.contrib.sites.models import Site

from dbtemplates.conf import settings
from dbtemplates.loader import Loader
from dbtemplates.models import Template, add_default_site
from dbtemplates.utils.cache import (
    cache,
    get_cache_backend,
    get_cache_key,
    set_and_return,
)
from dbtemplates.utils.template import get_template_source, check_template_syntax
from dbtemplates.management.commands import sync_templates


@receiver(setting_changed)
def handle_add_default_site(sender, setting, value, **kwargs):
    if setting == "DBTEMPLATES_ADD_DEFAULT_SITE":
        if value:
            post_save.connect(add_default_site, sender=Template)
        else:
            post_save.disconnect(add_default_site, sender=Template)


@contextmanager
def temptemplate(name: str, cleanup: bool = True):
    temp_template_dir = Path(tempfile.mkdtemp("dbtemplates"))
    temp_template_path = temp_template_dir / name
    try:
        yield temp_template_path
    finally:
        shutil.rmtree(temp_template_dir)


class DbTemplatesCacheTestCase(TestCase):
    def test_set_and_return(self):
        self.assertTrue(bool(cache))
        rtn = set_and_return(
            "this_is_the_cache_key", "cache test content", "cache display name"
        )
        self.assertEqual(rtn, ("cache test content", "cache display name"))
        self.assertEqual(cache.get("this_is_the_cache_key"), "cache test content")


class BaseDbTemplatesTestCase(TestCase):
    @modify_settings(
        TEMPLATES={
            "append": "dbtemplates.loader.Loader",
        },
    )
    def setUp(self):
        self.site1, created1 = Site.objects.get_or_create(
            domain="example.com", name="example.com"
        )
        self.site2, created2 = Site.objects.get_or_create(
            domain="example.org", name="example.org"
        )
        self.t1, _ = Template.objects.get_or_create(name="base.html", content="base")
        self.t2, _ = Template.objects.get_or_create(name="sub.html", content="sub")
        self.t2.sites.add(self.site2)


class DbTemplatesLoaderTestCase(BaseDbTemplatesTestCase):
    def test_load_and_store_template(self):
        from django.template.loader import _engine_list
        from django.core.cache import CacheKeyWarning

        loader = Loader(_engine_list()[0])
        with self.assertWarns(CacheKeyWarning):
            rtn = loader._load_and_store_template(
                "base.html", "base template cache key", self.site1
            )
        self.assertEqual(rtn, ("base", "dbtemplates:default:base.html:example.com"))

    @override_settings(DBTEMPLATES_ADD_DEFAULT_SITE=False)
    def test_load_templates_sites(self):
        t_site1 = Template.objects.create(
            name="copyright.html", content="(c) example.com"
        )
        t_site1.sites.add(self.site1)
        t_site2 = Template.objects.create(
            name="copyright.html", content="(c) example.org"
        )
        t_site2.sites.add(self.site2)

        new_site = Site.objects.create(domain="example.net", name="example.net")
        with self.settings(SITE_ID=new_site.id):
            Site.objects.clear_cache()

            self.assertRaises(
                TemplateDoesNotExist, loader.get_template, "copyright.html"
            )

    def test_load_templates(self):
        result = loader.get_template("base.html").render()
        self.assertEqual(result, "base")
        result2 = loader.get_template("sub.html").render()
        self.assertEqual(result2, "sub")

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


class DbTemplatesModelsTestCase(BaseDbTemplatesTestCase):
    def test_basics(self):
        self.assertQuerySetEqual(
            self.t1.sites.all(), Site.objects.filter(id=self.site1.id)
        )
        self.assertIn("base", self.t1.content)
        self.assertEqual(str(self.t1), self.t1.name)
        self.assertEqual(str(self.t2), self.t2.name)
        self.assertQuerySetEqual(
            Template.objects.filter(sites=self.site1),
            Template.objects.filter(id__in=[self.t1.id, self.t2.id]),
        )
        self.assertQuerySetEqual(
            self.t2.sites.all(),
            Site.objects.filter(id__in=[self.site1.id, self.site2.id]),
        )

    def test_populate(self):
        t0 = Template.objects.create(
            name="header.html", content="<h1>This is a header</h1>"
        )
        t0.populate()
        self.assertEqual(t0.content, "<h1>This is a header</h1>")
        t0.populate(name="header.html")
        self.assertEqual(t0.content, "<h1>This is a header</h1>")

        with temptemplate("temp_test.html") as temp_template_path:
            temp_template_path.write_text("temp test")
            (temp_template_path.parent / "temp_test_2.html").write_text("temp test 2")
            NEW_TEMPLATES = settings.TEMPLATES.copy()
            NEW_TEMPLATES[0]["DIRS"] = (temp_template_path.parent,)
            with self.settings(TEMPLATES=NEW_TEMPLATES):
                t1 = Template.objects.create(name="temp_test.html")
                t1.populate()
                self.assertEqual(t1.content, "temp test")
                t2 = Template.objects.create(name="temp_test.html")
                t2.populate(name="temp_test_2.html")
                self.assertEqual(t2.content, "temp test 2")
                t3 = Template.objects.create(name="temp_test_3.html")
                self.assertIsNone(t3.populate(name="temp_test_doesnt_exist.html"))
                self.assertEqual(t3.content, "")

    @override_settings(DBTEMPLATES_ADD_DEFAULT_SITE=False)
    def test_empty_sites(self):
        self.t3 = Template.objects.create(name="footer.html", content="footer")
        self.assertQuerySetEqual(self.t3.sites.all(), self.t3.sites.none())

    def test_error_templates_creation(self):
        call_command("create_error_templates", force=True, verbosity=0)
        self.assertQuerySetEqual(
            Template.objects.filter(sites=self.site1), Template.objects.filter()
        )
        self.assertTrue(Template.objects.filter(name="404.html").exists())

    def test_automatic_sync(self):
        admin_base_template = get_template_source("admin/base.html")
        template = Template.objects.create(name="admin/base.html")
        self.assertEqual(admin_base_template, template.content)

    def test_get_cache(self):
        self.assertTrue(isinstance(get_cache_backend(), BaseCache))

    def test_check_template_syntax(self):
        bad_template, _ = Template.objects.get_or_create(
            name="bad.html", content="{% if foo %}Bar"
        )
        good_template, _ = Template.objects.get_or_create(
            name="good.html", content="{% if foo %}Bar{% endif %}"
        )
        self.assertFalse(check_template_syntax(bad_template)[0])
        self.assertTrue(check_template_syntax(good_template)[0])

    def test_get_cache_name(self):
        self.assertEqual(
            get_cache_key("name with spaces"), "dbtemplates::name-with-spaces::1"
        )


class DbTemplatesSyncTemplatesCommandTestCase(TestCase):
    def test_sync_templates(self):
        with temptemplate("temp_test.html") as temp_template_path:
            temp_template_path.write_text("temp test", encoding="utf-8")
            NEW_TEMPLATES = settings.TEMPLATES.copy()
            NEW_TEMPLATES[0]["DIRS"] = sync_templates.DIRS = (
                temp_template_path.parent,
            )
            with self.settings(TEMPLATES=NEW_TEMPLATES):
                self.assertFalse(
                    Template.objects.filter(name="temp_test.html").exists()
                )
                call_command(
                    "sync_templates",
                    force=True,
                    verbosity=0,
                    overwrite=sync_templates.FILES_TO_DATABASE,
                )
                self.assertTrue(Template.objects.filter(name="temp_test.html").exists())

                t = Template.objects.get(name="temp_test.html")
                t.content = "temp test modified"
                t.save()
                call_command(
                    "sync_templates",
                    force=True,
                    verbosity=0,
                    overwrite=sync_templates.DATABASE_TO_FILES,
                )
                self.assertEqual(
                    "temp test modified", temp_template_path.read_text(encoding="utf-8")
                )

                call_command(
                    "sync_templates",
                    ext=".html",
                    app_first=True,
                    force=True,
                    verbosity=0,
                    delete=True,
                    overwrite=sync_templates.DATABASE_TO_FILES,
                )
                self.assertTrue(temp_template_path.exists())
                self.assertFalse(
                    Template.objects.filter(name="temp_test.html").exists()
                )
