import unittest

from tests.test_data_store import samples_data
from src.data_store.validator import SamplesValidator
from src.data_store.samples_data_model import samples_schema


class TestValidator(unittest.TestCase):

    def setUp(self):
        super(TestValidator, self).setUp()

        self.v = SamplesValidator(samples_schema)

    def tearDown(self):
        pass

    def test_validator(self):
        assert self.v.validate_document(samples_data) is True, self.v.errors
