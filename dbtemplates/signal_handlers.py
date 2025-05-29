from django.contrib.sites.models import Site
from django.db.models import Subquery
from django.db.utils import IntegrityError

from .models import Template


def verify_template_name_uniqueness_across_all_selected_sites(sender, **kwargs):
    if kwargs.get('action', None) == 'pre_add':
        if kwargs.get('reverse'):
            site = kwargs.get('instance', None)
            template_ids = kwargs.get('pk_set', None)

            template_names = Template.objects.filter(id__in=template_ids).values_list('name')
            if template := site.template_set.filter(name__in=Subquery(template_names)).first():
                raise IntegrityError(
                    f"Template with name '{template.name}' already exists for site '{site.name}'"
                )
        else:
            template = kwargs.get('instance', None)
            site_ids = kwargs.get('pk_set', None)
            if site := Site.objects.filter(id__in=site_ids, template__name=template.name).first():
                raise IntegrityError(
                    f"Template with name '{template.name}' already exists for site '{site.name}'"
                )
