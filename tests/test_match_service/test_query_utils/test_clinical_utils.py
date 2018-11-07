from tests.test_match_service import TestQueryUtilitiesShared
from src.services.match_service.query_utils.clinical_utils import ClinicalUtils
from src.utilities.settings import oncotree_all_solid_text, oncotree_all_liquid_text


class TestClinicalUtils(TestQueryUtilitiesShared):

    def setUp(self):
        super(TestClinicalUtils, self).setUp()

        self.c = ClinicalUtils()

    def tearDown(self):
        pass

    def test_text_from_node(self):

        res = self.c._text_from_node(nodes=['NSCLC'])
        assert res == ['Non-Small Cell Lung Cancer'], res

    def test_expand_oncotree_diagnosis(self):

        diagnoses = self.c.expand_oncotree_diagnosis(diagnosis='Non-Small Cell Lung Cancer')
        assert sorted(diagnoses) == sorted(self.all_nsclc_cancer_types), sorted(diagnoses)

    def test_expand_grouped_diagnoses(self):

        all_liquid_cancers = self.c.expand_grouped_diagnoses(diagnosis=oncotree_all_liquid_text)
        all_solid_cancers = self.c.expand_grouped_diagnoses(diagnosis=oncotree_all_solid_text)
        assert sorted(all_liquid_cancers) == self.all_liquid_cancer_types, sorted(all_liquid_cancers)
        assert sorted(all_solid_cancers) == self.all_solid_cancer_types, sorted(all_solid_cancers)
