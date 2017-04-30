from django.test import TestCase


class TestExecuteDryRun(TestCase):
    def test_collects_same_collections_as_live_mode(self):
        pass

    def test_doesnt_write_result_to_file(self):
        pass


class TestExecuteLive(TestCase):
    def test_gets_docs_for_each_discovered_collection(self):
        pass

    def test_writes_all_discovered_docs(self):
        pass

    def test_aborts_on_fatal_error(self):
        pass