from src.data_store import key_names as kn
from tests.test_match_service import TestQueryUtilitiesShared
from src.services.match_service.query_utils.clinical_queries import ClinicalQueries
from src.services.match_service.query_utils.clinical_projs import ClinicalProjs


class TestClinicalQueries(TestQueryUtilitiesShared):
    def setUp(self):
        super(TestClinicalQueries, self).setUp()

        self.cq = ClinicalQueries()
        self.cp = ClinicalProjs()
        self.db.testSamples.insert_many(self.test_cases)

    def tearDown(self):
        self.db.testSamples.drop()

    def test_create_oncotree_diagnosis_query(self):

        # query
        q1 = self.cq.create_oncotree_diagnosis_query(cancer_type='Lung', include=True)
        q2 = self.cq.create_oncotree_diagnosis_query(cancer_type='Lung', include=False)
        p1 = self.cp.create_oncotree_diagnosis_proj(proj=self.proj)
        p2 = self.cp.create_oncotree_diagnosis_proj(proj=self.proj)
        res1 = self._find(query=q1, proj=p1)
        res2 = self._find(query=q2, proj=p2)
        self._print(q1)
        self._print(p1)
        self._print(q2)
        self._print(p2)

        assert res1 is not None
        assert res2 is not None
        assert res1 == {
            kn.sample_id_col: 'TEST-SAMPLE-LUNG',
            kn.oncotree_primary_diagnosis_name_col: 'Lung'
        }, res1
        assert res2 == {
            kn.sample_id_col: 'TEST-SAMPLE-COLON',
            kn.oncotree_primary_diagnosis_name_col: 'Colon'
        }, res2


    def test_create_age_query(self):
        raise NotImplementedError

    def test_create_gender_query(self):
        raise NotImplementedError
