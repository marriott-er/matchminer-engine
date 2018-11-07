from src.data_store import key_names as kn
from tests.test_match_service import TestQueryUtilitiesShared
from src.services.match_service.query_utils.clinical_queries import ClinicalQueries


class TestClinicalQueries(TestQueryUtilitiesShared):
    def setUp(self):
        super(TestClinicalQueries, self).setUp()

        self.cq = ClinicalQueries()
        self.db.testSamples.insert_many(self.test_cases)

    def tearDown(self):
        self.db.testSamples.drop()

    def test_create_oncotree_diagnosis_query(self):

        q1 = self.cq.create_oncotree_diagnosis_query(cancer_type='Lung', include=True)
        q2 = self.cq.create_oncotree_diagnosis_query(cancer_type='Lung', include=False)
        res1 = self._find(q1)
        res2 = self._find(q2)

        assert res1 is not None
        assert res2 is not None
        assert res1[kn.sample_id_col] == 'TEST-SAMPLE-LUNG', res1
        assert res2[kn.sample_id_col] == 'TEST-SAMPLE-COLON', res2

    def test_create_age_query(self):
        raise NotImplementedError

    def test_create_gender_query(self):
        raise NotImplementedError
