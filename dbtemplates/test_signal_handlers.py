from django.contrib.sites.models import Site
from django.db.models.signals import m2m_changed
from django.db.utils import IntegrityError
from django.dispatch import receiver
from django.test import TestCase, override_settings
from django.test.signals import setting_changed

from dbtemplates.models import Template


@receiver(setting_changed)
def reload_modules_when_settings_change(sender, setting, value, enter, **kwargs):
    from .signal_handlers import verify_template_name_uniqueness_across_all_selected_sites
    if setting == 'DBTEMPLATES_UNIQUE' and value:
        if enter:
            m2m_changed.connect(verify_template_name_uniqueness_across_all_selected_sites)
        else:
            m2m_changed.disconnect(verify_template_name_uniqueness_across_all_selected_sites)


class VerifyTemplateUniqueness(TestCase):
    @classmethod
    def setUpTestData(cls):
        sites = Site.objects.bulk_create([
            Site(name="All", domain="all.example.com"),
            Site(name="1", domain="one.example.com"),
            Site(name="2", domain="two.example.com"),
            Site(name="3", domain="three.example.com"),
        ])

        templates = Template.objects.bulk_create([
            Template(name="Ayy", content="AAAA"),
            Template(name="Bee", content="BBBB"),
            Template(name="Sea", content="CCCC"),
            Template(name="Dee", content="AAAA"),
            Template(name="Eee", content="AAAA"),
            Template(name="Ayy", content="FFFF"),
            Template(name="Bee", content="GGGG"),
        ])

        for template in templates[:3]:
            template.sites.add(sites[0])

        templates[0].sites.add(sites[1])
        templates[1].sites.add(sites[2])
        templates[2].sites.add(sites[3])

        cls.sites = sites
        cls.templates = templates

    @override_settings(
        DBTEMPLATES_UNIQUE=True,
        DBTEMPLATES_ADD_DEFAULT_SITE=False,
    )
    def test_signal_handler_forward_unique_works(self):
        self.templates[0].sites.add(self.sites[2])
        self.templates[3].sites.add(self.sites[0])

    @override_settings(
        DBTEMPLATES_UNIQUE=True,
        DBTEMPLATES_ADD_DEFAULT_SITE=False,
    )
    def test_signal_handler_reverse_unique_works(self):
        self.sites[3].template_set.add(self.templates[1])

    @override_settings(
        DBTEMPLATES_UNIQUE=True,
        DBTEMPLATES_ADD_DEFAULT_SITE=False,
    )
    def test_signal_handler_forward_nonunique_prevented(self):
        with self.assertRaises(IntegrityError):
            self.templates[5].sites.add(self.sites[0])

    @override_settings(
        DBTEMPLATES_UNIQUE=True,
        DBTEMPLATES_ADD_DEFAULT_SITE=False,
    )
    def test_signal_handler_reverse_nonunique_prevented(self):
        with self.assertRaises(IntegrityError):
            self.sites[2].template_set.add(self.templates[6])
