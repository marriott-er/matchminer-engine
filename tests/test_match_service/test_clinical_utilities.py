import unittest

from tests.test_match_service import all_nsclc_cancer_types, all_liquid_cancer_types, all_solid_cancer_types
from src.utilities.settings import oncotree_all_solid_text, oncotree_all_liquid_text
from src.services.match_service.clinical_utilities import ClinicalUtilities


class TestClinicalUtilities(unittest.TestCase):

    def setUp(self):
        super(TestClinicalUtilities, self).setUp()

        self.c = ClinicalUtilities()

    def tearDown(self):
        pass

    def test_text_from_node(self):

        res = self.c._text_from_node(nodes=['NSCLC'])
        assert res == ['Non-Small Cell Lung Cancer'], res

    def test_expand_oncotree_diagnosis(self):

        diagnoses = self.c.expand_oncotree_diagnosis(diagnosis='Non-Small Cell Lung Cancer')
        assert sorted(diagnoses) == sorted(all_nsclc_cancer_types), sorted(diagnoses)

    def test_expand_grouped_diagnoses(self):

        all_liquid_cancers = self.c.expand_grouped_diagnoses(diagnosis=oncotree_all_liquid_text)
        all_solid_cancers = self.c.expand_grouped_diagnoses(diagnosis=oncotree_all_solid_text)
        assert sorted(all_liquid_cancers) == all_liquid_cancer_types, sorted(all_liquid_cancers)
        assert sorted(all_solid_cancers) == all_solid_cancer_types, sorted(all_solid_cancers)
