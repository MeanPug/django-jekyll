from django_jekyll.lib import fs
from django.conf import settings
import os


class ConfigParser(object):
    def __init__(self):
        self.defaults = {
            'JEKYLL_PROJECT_DIR': fs.search_parents_for_dirs(os.path.dirname(os.path.abspath(__file__)), ['site', 'jekyll']),
            'JEKYLL_PROJECT_STAGING_DIR': '/tmp/jekyll',
            'JEKYLL_COLLECTIONS_MODULE': 'jekyll',
            'JEKYLL_COLLECTIONS_INCLUDE_APPS': None,
            'JEKYLL_MAX_BATCH_SIZE': 1000,
            'JEKYLL_MAX_COLLECTION_SIZE': 10000,
        }

    def __getattr__(self, item):
        return getattr(settings, item, self.defaults[item])


config = ConfigParser()