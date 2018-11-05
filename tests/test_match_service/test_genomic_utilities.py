import unittest

from src.services.match_service.query_utilities.genomic_utilities import GenomicUtilities
from tests.test_match_service import *


class TestGenomicUtilities(unittest.TestCase):

    def setUp(self):
        super(TestGenomicUtilities, self).setUp()

        self.g = GenomicUtilities()

    def tearDown(self):
        pass
