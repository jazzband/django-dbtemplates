from django.core.management.base import CommandError, NoArgsCommand

from dbtemplates.models import Template
from dbtemplates.utils.template import check_template_syntax

class Command(NoArgsCommand):
    help = "Ensures templates stored in the database don't have syntax errors."

    def handle_noargs(self, **options):
        errors = []
        for template in Template.objects.all():
            valid, error = check_template_syntax(template)
            if not valid:
                errors.append('%s: %s' % (template.name, error))
        if errors:
            raise CommandError(
                'Some templates contained errors\n%s' % '\n'.join(errors))
        # NOTE: printing instead of using self.stdout.write to maintain
        # Django 1.2 compatibility
        print('OK')
