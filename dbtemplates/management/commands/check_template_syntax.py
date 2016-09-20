from django.core.management.base import CommandError, BaseCommand

from dbtemplates.models import Template
from dbtemplates.utils.template import check_template_syntax


class Command(BaseCommand):
    help = "Ensures templates stored in the database don't have syntax errors."

    def handle(self, **options):
        errors = []
        for template in Template.objects.all():
            valid, error = check_template_syntax(template)
            if not valid:
                errors.append('%s: %s' % (template.name, error))
        if errors:
            raise CommandError(
                'Some templates contained errors\n%s' % '\n'.join(errors))
        self.stdout.write('OK')
