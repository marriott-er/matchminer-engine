import unittest

from src.services.match_service.query_utils.genomic_utils import GenomicUtils
from tests.test_match_service import *


class TestGenomicUtils(unittest.TestCase):

    def setUp(self):
        super(TestGenomicUtils, self).setUp()

        self.g = GenomicUtils()

    def tearDown(self):
        pass
