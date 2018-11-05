from src.utilities import settings as s
from src.data_store import key_names as kn
from tests.test_match_service import TestQueryUtilitiesShared
from src.services.match_service.query_utilities.query_utilities import QueryUtilities


class TestQueryUtilities(TestQueryUtilitiesShared):

    def setUp(self):
        super(TestQueryUtilities, self).setUp()

        self.q = QueryUtilities()
        self.db.testSamples.insert_many(self.test_cases)

    def tearDown(self):
        self.db.testSamples.drop()

    def test_handle_exclusion_queries(self):

        inclusion_query = {kn.mutation_list_col: {'$elemMatch': {kn.hugo_symbol_col: {'$eq': 'BRAF'}}}}
        exclusion_query = {kn.mutation_list_col: {'$elemMatch': {kn.hugo_symbol_col: {'$ne': 'BRAF'}}}}
        q1 = self.q.handle_exclusion_queries(query=inclusion_query,
                                             variant_category=s.variant_category_mutation_val,
                                             include=True)
        q2 = self.q.handle_exclusion_queries(query=exclusion_query,
                                             variant_category=s.variant_category_mutation_val,
                                             include=False)
        res1 = self._findall(q1)
        res2 = self._findall(q2)

        assert len(res1) == 1, res1
        assert res1[0][kn.sample_id_col] == 'TEST-SAMPLE-BRAF'
        assert len(res2) == 2, res2
        assert sorted([i[kn.sample_id_col] for i in res2]) == sorted(['TEST-SAMPLE-EGFR', 'TEST-SAMPLE-NO-MUTATION']), \
            res2

    def test_create_no_variants_query(self):

        q1 = self.q.create_no_variants_query(variant_category=s.variant_category_mutation_val)
        q2 = self.q.create_no_variants_query(variant_category=s.variant_category_cnv_val)
        q3 = self.q.create_no_variants_query(variant_category=s.variant_category_sv_val)
        res1 = self._findall(q1)
        res2 = self._findall(q2)
        res3 = self._findall(q3)

        assert len(res1) == 1, res1
        assert res1[0][kn.sample_id_col] == 'TEST-SAMPLE-NO-MUTATION', res1[0][kn.sample_id_col]
        assert len(res2) == 0, res2
        assert len(res3) == 0, res3
