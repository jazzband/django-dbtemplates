#!/usr/bin/env python
import os
import sys

def setup_environ():
    """
    Configure the runtime environment.
    """
    project_directory = os.getcwd()
    project_name = os.path.basename(project_directory)
    sys.path.append(os.path.join(project_directory, '..'))
    project_module = __import__(project_name, {}, {}, [''])
    sys.path.pop()

    # Set DJANGO_SETTINGS_MODULE appropriately.
    os.environ['DJANGO_SETTINGS_MODULE'] = '%s.settings' % project_name
    return project_name

def synctemplates(extension=".html", overwrite=False):
    """
    Helper function for syncing templates in TEMPLATES_DIRS with the
    dbtemplates contrib app.
    """
    from django.contrib.sites.models import Site
    from django.template import TemplateDoesNotExist
    from dbtemplates.models import Template
    
    tried = []
    synced = []
    existing = []
    overwritten = []
    
    try:
        site = Site.objects.get_current()
    except:
        site = None
    
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

def main():
    try:
        project_name = setup_environ()
        print "Loading settings from project '%s'.. done." % project_name
        synctemplates()
    except ImportError, e:
        print "Please make sure a settings.py file exists in the current directory."
        print e
        sys.exit(0)
    except OSError, e:
        print e
        sys.exit(0)
    except:
        sys.exit(0)

if __name__ == "__main__":
    main()