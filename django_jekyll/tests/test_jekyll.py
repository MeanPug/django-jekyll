from django.test import TestCase


class TestGetDocs(TestCase):
    def test_parses_retrieved_models(self):
        pass

    def test_max_collection_size_reached_raises_error(self):
        pass

    def test_finishes_when_all_docs_returned(self):
        pass


class TestParseDoc(TestCase):
    def test_parse_string_field(self):
        pass

    def test_parse_integer_field(self):
        pass

    def test_parse_array_field(self):
        pass

    def test_parse_document_missing_content_field_raises_error(self):
        pass

    def test_parse_document_missing_filename_field_raises_error(self):
        pass

    def test_calls_parse_field_for_each_parsed_name_meta_map(self):
        pass


class TestParseField(TestCase):
    def test_parse_direct_lookup(self):
        pass

    def test_parse_one_to_one_field(self):
        pass

    def test_parse_one_to_many_field(self):
        pass

    def test_parse_many_to_one_field(self):
        pass

    def test_parse_many_to_one_field_with_related_name(self):
        pass

    def test_parse_many_to_many_field(self):
        pass

    def test_parse_one_to_many_with_related_lookup(self):
        # field name like 'client__name'
        pass