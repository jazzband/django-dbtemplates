from pathlib import Path

from dbtemplates.models import Template
from django.contrib.sites.models import Site
from django.core.management.base import BaseCommand, CommandError
from django.template.loader import _engine_list
from django.template.utils import get_app_template_dirs

ALWAYS_ASK, FILES_TO_DATABASE, DATABASE_TO_FILES = ("0", "1", "2")

DIRS = []
for engine in _engine_list():
    DIRS.extend(engine.dirs)
DIRS = tuple(DIRS)
app_template_dirs = get_app_template_dirs("templates")


class Command(BaseCommand):
    help = "Syncs file system templates with the database bidirectionally."

    def add_arguments(self, parser):
        parser.add_argument(
            "-e",
            "--ext",
            dest="ext",
            action="store",
            default="html",
            help="extension of the files you want to "
            "sync with the database [default: %(default)s]",
        )
        parser.add_argument(
            "-f",
            "--force",
            action="store_true",
            dest="force",
            default=False,
            help="overwrite existing database templates",
        )
        parser.add_argument(
            "-o",
            "--overwrite",
            action="store",
            dest="overwrite",
            default="0",
            help="'0' - ask always, '1' - overwrite database "
            "templates from template files, '2' - overwrite "
            "template files from database templates",
        )
        parser.add_argument(
            "-a",
            "--app-first",
            action="store_true",
            dest="app_first",
            default=False,
            help="look for templates in applications "
            "directories before project templates",
        )
        parser.add_argument(
            "-d",
            "--delete",
            action="store_true",
            dest="delete",
            default=False,
            help="Delete templates after syncing",
        )

    def handle(self, **options):
        extension = options.get("ext")
        force = options.get("force")
        overwrite = options.get("overwrite")
        app_first = options.get("app_first")
        delete = options.get("delete")

        if not extension.startswith("."):
            extension = f".{extension}"

        try:
            site = Site.objects.get_current()
        except Exception:
            raise CommandError(
                "Please make sure to have the sites contrib "
                "app installed and setup with a site object"
            )

        if app_first:
            tpl_dirs = app_template_dirs + DIRS
        else:
            tpl_dirs = DIRS + app_template_dirs
        templatedirs = [Path(d) for d in tpl_dirs if Path(d).is_dir()]

        for templatedir in templatedirs:
            for dirpath, subdirs, filenames in templatedir.walk(follow_symlinks=True):
                for f in [
                    f
                    for f in filenames
                    if f.endswith(extension) and not f.startswith(".")
                ]:
                    path = dirpath / f
                    name = path.relative_to(templatedir)
                    try:
                        t = Template.on_site.get(name__exact=name)
                    except Template.DoesNotExist:
                        if not force:
                            confirm = input(
                                "\nA '%s' template doesn't exist in the "
                                "database.\nCreate it with '%s'?"
                                " (y/[n]): "
                                "" % (name, path)
                            )
                        if force or confirm.lower().startswith("y"):
                            t = Template.objects.create(
                                name=name, content=path.read_text(encoding="utf-8")
                            )
                            t.sites.add(site)
                    else:
                        while True:
                            if overwrite == ALWAYS_ASK:
                                _i = (
                                    "\n%(template)s exists in the database.\n"
                                    "(1) Overwrite %(template)s with '%(path)s'\n"  # noqa
                                    "(2) Overwrite '%(path)s' with %(template)s\n"  # noqa
                                    "Type 1 or 2 or press <Enter> to skip: "
                                    % {"template": t.__repr__(), "path": path}
                                )

                                confirm = input(_i)
                            else:
                                confirm = overwrite
                            if confirm in (
                                "",
                                FILES_TO_DATABASE,
                                DATABASE_TO_FILES,
                            ):
                                if confirm == FILES_TO_DATABASE:
                                    t.content = path.read_text(encoding="utf-8")
                                    t.save()
                                    t.sites.add(site)
                                    if delete:
                                        try:
                                            path.unlink(missing_ok=True)
                                        except OSError:
                                            raise CommandError(
                                                f"Couldn't delete {path}"
                                            )
                                elif confirm == DATABASE_TO_FILES:
                                    path.write_text(t.content, encoding="utf-8")
                                    if delete:
                                        t.delete()
                                break
