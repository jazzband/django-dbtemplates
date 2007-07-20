"""
Helper function for syncing templates in TEMPLATES_DIRS with the dbtemplates
contrib app.
"""

from django.conf import settings
from django.template import TemplateDoesNotExist
from django.contrib.dbtemplates.models import Template
from django.contrib.sites.models import Site

import os
import sys

try:
    site = Site.objects.get_current()
except:
    site = None

def synctemplates(extension=".html", overwrite=False):
    """
    Helper function for syncing templates in TEMPLATES_DIRS with the
    dbtemplates contrib app.
    """
    tried = []
    synced = []
    existing = []
    overwritten = []
    
    if site is not None:
        for template_dir in settings.TEMPLATE_DIRS:
            if os.path.isdir(template_dir):
                for dirpath, subdirs, filenames in os.walk(template_dir):
                    for file in filenames:
                        if file.endswith(extension) and not file.startswith("."):
                            filepath = os.path.join(dirpath, file)
                            filename = filepath.split(template_dir)[1][1:]
                            try:
                                try:
                                    t = Template.objects.get(name__exact=filename)
                                except Template.DoesNotExist:
                                    filecontent = open(filepath, "r").read()
                                    t = Template(name=filename, content=filecontent)
                                    t.save()
                                    t.sites.add(site)
                                    synced.append(filename)
                                else:
                                    if overwrite:
                                        t.content = open(filepath, "r").read()
                                        t.save()
                                        t.sites.add(site)
                                        overwritten.append(t.name)
                                    else:
                                        existing.append(t.name)
                            except IOError:
                                tried.append(filepath)
                            except:
                                raise TemplateDoesNotExist

        if len(existing) > 0:
            print "\nAlready existing templates:"
            for _existing in existing:
                print _existing

        if len(overwritten) > 0:
            print "\nOverwritten existing templates:"
            for _replaced in overwritten:
                print _replaced

        if len(synced) > 0:
            print "\nSuccessfully synced templates:"
            for _synced in synced:
                print _synced

        if len(tried) > 0:
            print "\nTried to sync but failed:"
            for _tried in tried:
                print _tried

if __name__ == "__main__":
    synctemplates()