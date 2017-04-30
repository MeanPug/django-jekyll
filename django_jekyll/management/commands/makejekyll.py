from django.core.management.base import BaseCommand, CommandError
from django_jekyll.jekyll.collection import discover_collections, atomic_write_collection
from django_jekyll.lib import fs
from django_jekyll import exceptions, config
import os


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
        #TODO: Add prompt here asking user to confirm location of build (to JEKYLL_PROJECT_DIR), since this is a destructive op

        for collection in discover_collections():
            self.stdout.write('discovered %s, preparing to generate Jekyll docs..' % collection)

            message += '\n\n'
            message += str(collection)
            message += '------------'

            try:
                num_written = atomic_write_collection(collection, config.JEKYLL_PROJECT_STAGING_DIR) if not options['dry_run'] else len(list(collection.docs))
                message += '* %s docs generated for %s' % (num_written, collection)
                if options['dry_run']:
                    message += ' (DRY)'
            except (exceptions.CollectionSizeExceeded, exceptions.DocGenerationFailure) as exc:
                raise CommandError(str(exc))

        # at this point, we've written our jekyll files to a staging build dir. Now copy the staging folder contents to their live counterparts
        if not options['dry_run']:
            self.stdout.write('docs generation success, now transferring staging contents to project folder...')

            # for d in fs.list_dir(config.JEKYLL_PROJECT_STAGING_DIR):
            #     if fs.is_dir(os.path.join(config.JEKYLL_PROJECT_DIR, d)):
            #         fs.remove_dir(os.path.join(config.JEKYLL_PROJECT_DIR, d))
            #
            #     fs.move_dir(os.path.join(config.JEKYLL_PROJECT_STAGING_DIR, d), config.JEKYLL_PROJECT_DIR)
            #
            #     self.stdout.write('moved staging dir %s to project dir %s' % (d, config.JEKYLL_PROJECT_DIR))

        self.stdout.write(self.style.SUCCESS(message))