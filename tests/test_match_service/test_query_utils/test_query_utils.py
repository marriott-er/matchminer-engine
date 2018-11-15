from src.utilities import settings as s
from src.data_store import key_names as kn
from tests.test_match_service import TestQueryUtilitiesShared
from src.services.match_service.query_utils.query_utils import QueryUtils


class TestQueryUtils(TestQueryUtilitiesShared):

    def setUp(self):
        super(TestQueryUtils, self).setUp()

        self.q = QueryUtils()
        self.db.testSamples.insert_many(self.test_cases)

    def tearDown(self):
        self.db.testSamples.drop()

    def test_create_inclusion_query(self):

        res = self.q.create_inclusion_query(variant_category=kn.mutation_list_col,
                                            key=kn.hugo_symbol_col,
                                            val='BRAF')
        assert res == {kn.mutation_list_col: {'$elemMatch': {kn.hugo_symbol_col: 'BRAF'}}}

    def test_create_exclusion_query(self):

        res = self.q.create_exclusion_query(variant_category=kn.mutation_list_col,
                                            key=kn.hugo_symbol_col,
                                            val='BRAF')
        assert res == {
            '$or': [
                {kn.mutation_list_col: {'$not': {'$elemMatch': {kn.hugo_symbol_col: 'BRAF'}}}},
                {kn.mutation_list_col: []},
                {kn.mutation_list_col: {'$exists': False}}
            ]
        }
