from django.utils.text import slugify
from django.conf import settings
from django_jekyll import config, exceptions
from django_jekyll.jekyll.doc import JekyllDocument
from django_jekyll.lib import fs
import re
import logging
import os
import inspect

logger = logging.getLogger(__name__)


class JekyllCollection(object):
    """ a Jekyll Collection."""
    @property
    def docs(self):
        """ generate the documents to be written out
        :return: `generator` of `docs.Document` to be written out
        """
        counter = 0

        while True:
            batch = list(self.queryset()[counter:counter + config.JEKYLL_MAX_BATCH_SIZE])

            if counter + len(batch) > config.JEKYLL_MAX_COLLECTION_SIZE:
                raise exceptions.CollectionSizeExceeded("%s exceeded size constraint of %s (has %s)!" % (self, config.JEKYLL_MAX_COLLECTION_SIZE, counter + len(batch)))
            elif len(batch) == 0:
                return

            parsed = self.parse_to_docs(batch)

            for p in parsed:
                yield p

            counter += config.JEKYLL_MAX_BATCH_SIZE

    def queryset(self):
        """ base queryset of models to generate collection from.
        :return:
        """
        return self.model.objects.all()

    def parse_to_docs(self, models):
        """ parse the given list of Models to Document instances
        :param models:
        :return:
        """
        return map(self.parse_to_document, models)

    def parse_to_document(self, model):
        field_val_map = {}
        field_meta_map = {}

        model_fields = {f.name: f for f in model._meta.get_fields(include_hidden=True)}

        for field in self.fields:
            if field in model_fields:
                field_meta_map[field] = model_fields[field]
            else:
                # its possible we're dealing with a field like 'client__name'
                field_parts = self._related_lookup_parts(field)

                if field_parts and field_parts[0] in model_fields:
                    field_meta_map[field] = model_fields[field_parts[0]]

        # for each field, run it through a field parser to get the value of the field
        for fname, fmeta in field_meta_map.items():
            field_val_map[fname] = self.parse_field(model, fname, fmeta)

        # if we want the doc to have no content
        if self.content_field is None:
            field_val_map[self.content_field] = ''

        # check that all required fields are present, raising errors if not
        if self.content_field not in field_val_map:
            raise exceptions.DocGenerationFailure("content_field %s wasn't found on model %s" % (self.content_field, model))
        elif type(self.filename_field) is str and self.filename_field not in field_meta_map:
            raise exceptions.DocGenerationFailure("filename_field %s is a string and wasn't found on model %s, either make it a function or use a different field" % (self.filename_field, model))

        content = field_val_map.pop(self.content_field)

        return JekyllDocument(content,
                              filename=field_val_map[self.filename_field] if type(self.filename_field) is str else self.filename_field(model),
                              frontmatter_data=field_val_map)

    def parse_field(self, model, field_name, field_meta):
        """ given a model, a field name (can include lookups like 'client__name', 'client__goal__name', etc.), and the
        field_meta object for the immediate field related to the field_name (so for simple case of 'name', this would
        be the 'name' field meta object, for the complex case of 'client__name', this would be the 'client' field meta
        object, and for 'client__goal__name', this would also be the 'client' field meta object), parse the value of the
        field given by field_name from the model and return it
        :param model:
        :param field_name:
        :param field_meta:
        :return:
        """
        if field_meta.concrete and not (field_meta.is_relation or field_meta.one_to_one or field_meta.many_to_one or field_meta.one_to_many or field_meta.many_to_many):
            # concrete field
            return getattr(model, field_name)
        elif field_meta.many_to_many and not field_meta.auto_created:
            # many to many
            return list(getattr(model, field_name).values_list('id', flat=True))
        elif field_meta.one_to_many:
            # one to many
            return list(getattr(model, field_name).values_list('id', flat=True))
        elif field_meta.one_to_one or field_meta.many_to_one or field_meta.related_model:
            # can be one-to-one, many-to-one, these we have to look for related lookups on
            field_parts = self._related_lookup_parts(field_name)

            if field_parts:
                related_model = getattr(model, field_parts[0])
                return self.parse_field(related_model, field_parts[1], related_model._meta.get_field(field_parts[1]))
            else:
                return getattr(model, '%s_id' % field_name)

    ##-- Helpers --##
    def _related_lookup_parts(self, field_name):
        related_lookup_pattern = '^(\w(?:[0-9A-Za-z]|_[0-9A-Za-z])*)__(\w.*)'

        match = re.match(related_lookup_pattern, field_name)

        if not match:
            return []
        else:
            head = match.groups()[0]
            tail = match.groups()[1]

            remaining_parts = self._related_lookup_parts(tail)
            return [head] + remaining_parts if remaining_parts else [head, tail]

    ##-- Accessors --##
    @property
    def model(self):
        return self.Meta.model

    @property
    def fields(self):
        return self.Meta.fields

    @property
    def content_field(self):
        return getattr(self.Meta, 'content_field')

    @property
    def filename_field(self):
        return getattr(self.Meta, 'filename_field', str)

    @property
    def jekyll_label(self):
        return getattr(self.Meta, 'jekyll_label', slugify(self.model.__name__).replace('-', '_'))

    def __str__(self):
        return 'Collection (%s -> %s)' % (self.model.__name__, self.jekyll_label)

    class Meta:
        model = None
        fields = []
        # the name of the field on the model containing the data to be used as the content of the documents
        content_field = 'text'
        # the name of a field or a function to be used to set the filenames on the documents of the collection
        filename_field = None
        jekyll_label = None


def discover_collections():
    """ search through the projects installed apps, for each looking for the presence of a jekyll.py file (or whatever
    the overriden name is in config.JEKYLL_COLLECTIONS_FILENAME)
    :return: `generator` of `Collection` discovered in each of the collection files found
    """
    collections = []
    apps = config.JEKYLL_COLLECTIONS_INCLUDE_APPS or settings.INSTALLED_APPS

    for app in apps:
        try:
            jekyll_collection_module = __import__('%s.%s' % (app, config.JEKYLL_COLLECTIONS_MODULE), fromlist=[app])
        except ImportError:
            continue

        for name, cls in inspect.getmembers(jekyll_collection_module):
            if inspect.isclass(cls) and cls != JekyllCollection and issubclass(cls, JekyllCollection):
                collections.append(cls())

    return collections


def atomic_write_collection(collection, build_dir):
    """ given a collection, atomically write the collections' data to location. Meaning, if any document in the collection
    fails to generate/write, the entire operation aborts
    :param collection:
    :return:
    """
    counter = 0
    collection_dir = os.path.join(build_dir, '_' + collection.jekyll_label)

    try:
        for doc in collection.docs:
            doc.write(collection_dir)
            counter += 1
    except (exceptions.DocGenerationFailure, exceptions.CollectionSizeExceeded) as exc:
        logger.error('atomic write failed! (%s)' % str(exc))
        fs.remove_dir(collection_dir)
        raise exc

    return counter