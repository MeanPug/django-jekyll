from django.core.management.base import BaseCommand, CommandError
from django_jekyll.jekyll.collection import discover_collections
from django_jekyll.lib import fs
from django_jekyll import exceptions


class Command(BaseCommand):
    help = 'Find all defined collections and write them to your Jekyll project'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry',
            action='store_true',
            dest='dry_run',
            default=False,
            help='Run the build as a dry run (generate collections and print some stats about them to stdout)'
        )

    def handle(self, *args, **options):
        message = ''

        for collection in discover_collections():
            self.stdout.write('discovered %s, preparing to generate Jekyll docs..' % collection)

            message += str(collection)
            message += '------------'

            docs = collection.docs

            try:
                num_written = fs.atomic_write(docs) if not options['dry_run'] else len(list(docs))
                message += '* %s docs generated for %s' % (num_written, collection)
                if options['dry_run']:
                    message += ' (DRY)\n\n'
            except (exceptions.CollectionSizeExceeded, exceptions.DocGenerationFailure) as exc:
                raise CommandError(str(exc))

        self.stdout.write(self.style.SUCCESS(message))