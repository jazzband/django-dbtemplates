#!/usr/bin/env python
import os
import sys
from optparse import OptionParser

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
    return project_name, project_module

def synctemplates(project_module, extension, overwrite):
    """
    Helper function for syncing templates in TEMPLATES_DIRS with the
    dbtemplates contrib app.
    """
    from django.contrib.sites.models import Site
    from django.template import TemplateDoesNotExist
    from dbtemplates.models import Template
    
    if not extension.startswith("."):
        extension = ".%s" % extension
    
    tried = []
    synced = []
    existing = []
    overwritten = []
    
    try:
        site = Site.objects.get_current()
    except:
        site = None
    
    if site is not None:
        if type(project_module.settings.TEMPLATE_DIRS) in (tuple, list):
            for template_dir in project_module.settings.TEMPLATE_DIRS:
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
                print "Already existing templates (use --force to overwrite):"
                for e in existing:
                    print e

            if len(overwritten) > 0:
                print "Overwritten existing templates:"
                for o in overwritten:
                    print o

            if len(synced) > 0:
                print "Successfully synced templates:"
                for s in synced:
                    print s

            if len(tried) > 0:
                print "Tried to sync but failed:"
                for t in tried:
                    print t
        else:
            print "Please make sure settings.TEMPLATE_DIRS is a list or tuple."

def main((options, args)):
    try:
        project_name, project_module = setup_environ()
        print "Loading settings from project '%s'.. done." % project_name
        synctemplates(project_module, options.ext, options.overwrite)
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
    parser = OptionParser()
    parser.add_option("-e", "--ext", dest="ext", action="store",
                      help="file extension of the files you want to sync with the database [default: %default]",
                      type="string", default="html")
    parser.add_option("-f", "--force",
                      action="store_true", dest="overwrite", default=False,
                      help="overwrite existing database templates")
    main(parser.parse_args())