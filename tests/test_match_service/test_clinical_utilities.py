import unittest

from src.services.match_service.clinical_utilities import ClinicalUtilities


class TestClinical(unittest.TestCase):

    def setUp(self):
        super(TestClinical, self).setUp()

        self.c = ClinicalUtilities()

    def tearDown(self):
        pass

    def test_text_from_node(self):

        res = self.c._text_from_node(nodes=['LUNG'])
        print res

    def test_expand_oncotree_diagnosis(self):

        diagnoses = self.c.expand_oncotree_diagnosis(diagnosis='Lung')
        print diagnoses
        # todo finish

    def test_expand_grouped_diagnoses(self):
        raise NotImplementedError