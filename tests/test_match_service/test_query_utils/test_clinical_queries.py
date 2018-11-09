from src.data_store import key_names as kn
from tests.test_match_service import TestQueryUtilitiesShared
from src.services.match_service.query_utils.clinical_queries import ClinicalQueries


class TestClinicalQueries(TestQueryUtilitiesShared):
    def setUp(self):
        super(TestClinicalQueries, self).setUp()

        self.cq = ClinicalQueries()

    def tearDown(self):
        self.db.testSamples.drop()

    def test_create_oncotree_diagnosis_query(self):

        # set up
        self.db.testSamples.insert_many([
            self.test_case_lung,
            self.test_case_colon
        ])

        # create query
        q1 = self.cq.create_oncotree_diagnosis_query(cancer_type='Lung', include=True)
        q2 = self.cq.create_oncotree_diagnosis_query(cancer_type='Lung', include=False)
        res1 = self._find(q1)
        res2 = self._find(q2)
        self._print(q1)
        self._print(q2)

        # assertions
        assert res1 is not None
        assert res2 is not None
        assert res1 == {kn.sample_id_col: 'TEST-SAMPLE-LUNG'}, res1
        assert res2 == {kn.sample_id_col: 'TEST-SAMPLE-COLON'}, res2

        # clean up
        self.db.testSamples.drop()

    def test_create_age_query(self):

        # set up
        self.db.testSamples.insert_many([
            self.test_case_child,
            self.test_case_adult
        ])

        # create query
        q1 = self.cq.create_age_query(age='>=17')
        q2 = self.cq.create_age_query(age='<17')
        res1 = self._find(q1)
        res2 = self._find(q2)
        self._print(q1)
        self._print(q2)

        # assertions
        assert res1 is not None
        assert res2 is not None
        assert res1 == {kn.sample_id_col: 'TEST-SAMPLE-ADULT'}, res1
        assert res2 == {kn.sample_id_col: 'TEST-SAMPLE-CHILD'}, res2

        # clean up
        self.db.testSamples.drop()

    def test_create_gender_query(self):

        # set up
        self.db.testSamples.insert_many([
            self.test_case_female,
            self.test_case_male
        ])

        # create query
        q1 = self.cq.create_gender_query(gender='Male')
        q2 = self.cq.create_gender_query(gender='Female')
        res1 = self._find(q1)
        res2 = self._find(q2)
        self._print(q1)
        self._print(q2)

        # assertions
        assert res1 is not None
        assert res2 is not None
        assert res1 == {kn.sample_id_col: 'TEST-SAMPLE-MALE'}, res1
        assert res2 == {kn.sample_id_col: 'TEST-SAMPLE-FEMALE'}, res2

        # clean up
        self.db.testSamples.drop()
