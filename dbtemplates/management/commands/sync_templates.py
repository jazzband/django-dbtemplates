from fnmatch import filter as fnmatch_filter
import os
import codecs
from optparse import make_option

from django.contrib.sites.models import Site
from django.core.management.base import CommandError, NoArgsCommand
from django.template.loaders.app_directories import app_template_dirs

from dbtemplates.conf import settings
from dbtemplates.models import Template

ALWAYS_ASK, FILES_TO_DATABASE, DATABASE_TO_FILES = ('0', '1', '2')


class Command(NoArgsCommand):
    help = "Syncs file system templates with the database bidirectionally."
    option_list = NoArgsCommand.option_list + (
        make_option("-e", "--ext",
                    dest="ext", action="store", default="html",
                    help="extension of the files you want to "
                         "sync with the database [default: %default]"),
        make_option("-f", "--force",
                    action="store_true", dest="force", default=False,
                    help="overwrite existing database templates"),
        make_option("-o", "--overwrite",
                    action="store", dest="overwrite", default='0',
                    help="'0' - ask always, '1' - overwrite database "
                         "templates from template files, '2' - overwrite "
                         "template files from database templates"),
        make_option("-a", "--app-first",
                    action="store_true", dest="app_first", default=False,
                    help="look for templates in applications "
                         "directories before project templates"),
        make_option("-d", "--delete",
                    action="store_true", dest="delete", default=False,
                    help="Delete templates after syncing"),
        make_option("--exclude",
                    action="append", dest="exclude", default=[],
                    help="Directory patterns(`fnmatch`) to be excluded"),

        make_option("--only",
                    action="append", dest="only", default=[],
                    help="Directory patterns(`fnmatch`) to be processed"))

    def handle_noargs(self, **options):
        extension = options.get('ext')
        force = options.get('force')
        overwrite = options.get('overwrite')
        app_first = options.get('app_first')
        delete = options.get('delete')
        exclude = options.get('exclude')
        only = options.get('only')

        if not extension.startswith("."):
            extension = ".%s" % extension

        try:
            site = Site.objects.get_current()
        except:
            raise CommandError("Please make sure to have the sites contrib "
                               "app installed and setup with a site object")

        if not type(settings.TEMPLATE_DIRS) in (tuple, list):
            raise CommandError("Please make sure settings.TEMPLATE_DIRS is a "
                               "list or tuple.")

        if app_first:
            tpl_dirs = app_template_dirs + settings.TEMPLATE_DIRS
        else:
            tpl_dirs = settings.TEMPLATE_DIRS + app_template_dirs
        templatedirs = set([d for d in tpl_dirs if os.path.isdir(d)])

        for pattern in only:
            templatedirs = fnmatch_filter(templatedirs, pattern)

        for pattern in exclude:
            templatedirs = templatedirs - set(fnmatch_filter(templatedirs, pattern))

        for templatedir in templatedirs:
            for dirpath, subdirs, filenames in os.walk(templatedir):
                for f in [f for f in filenames
                          if f.endswith(extension) and not f.startswith(".")]:
                    path = os.path.join(dirpath, f)
                    name = path.split(templatedir)[1]
                    if name.startswith('/'):
                        name = name[1:]
                    try:
                        t = Template.on_site.get(name__exact=name)
                    except Template.DoesNotExist:
                        if not force:
                            confirm = raw_input(
                                "\nA '%s' template doesn't exist in the "
                                "database.\nCreate it with '%s'?"
                                " (y/[n]): """ % (name, path))
                        if force or confirm.lower().startswith('y'):
                            t = Template(name=name,
                                         content=codecs.open(path, "r").read())
                            t.save()
                            t.sites.add(site)
                    else:
                        while 1:
                            if overwrite == ALWAYS_ASK:
                                confirm = raw_input(
                                    "\n%(template)s exists in the database.\n"
                                    "(1) Overwrite %(template)s with '%(path)s'\n"
                                    "(2) Overwrite '%(path)s' with %(template)s\n"
                                    "Type 1 or 2 or press <Enter> to skip: " %
                                    {'template': t.__repr__(), 'path': path})
                            else:
                                confirm = overwrite
                            if confirm in ('', FILES_TO_DATABASE,
                                           DATABASE_TO_FILES):
                                if confirm == FILES_TO_DATABASE:
                                    t.content = codecs.open(path, 'r').read()
                                    t.save()
                                    t.sites.add(site)
                                    if delete:
                                        try:
                                            os.remove(path)
                                        except OSError:
                                            raise CommandError(u"Couldn't delete %s" % path)
                                elif confirm == DATABASE_TO_FILES:
                                    f = codecs.open(path, 'w', 'utf-8')
                                    try:
                                        f.write(t.content)
                                    finally:
                                        f.close()
                                    if delete:
                                        t.delete()
                                break
