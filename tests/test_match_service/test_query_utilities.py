import unittest

from src.utilities import settings as s
s.MONGO_URI = 'mongodb://localhost:27017'
s.MONGO_DBNAME = 'matchminer'

from src.utilities.utilities import get_db
from tests.test_match_service import *
from src.data_store import key_names as kn
from src.services.match_service.query_utilities import QueryUtilities


class TestQueryUtilities(unittest.TestCase):

    def setUp(self):
        super(TestQueryUtilities, self).setUp()

        self.q = QueryUtilities()
        self.db = get_db(mongo_uri=s.MONGO_URI, mongo_dbname=s.MONGO_DBNAME)
        self.proj = {kn.sample_id_col: 1}

        test_cases = [test_case_lung, test_case_colon]
        self.db.testSamples.insert_many(test_cases)

    def tearDown(self):
        self.db.testSamples.drop()

    def _find(self, query):
        return self.db.testSamples.find_one(query, self.proj)

    def test_expand_query_to_list(self):

        res1 = self.q._expand_query_to_list(new_val=['Lung Type 1', 'Lung Type 2'], include=True)
        res2 = self.q._expand_query_to_list(new_val=['Lung Type 1', 'Lung Type 2'], include=False)
        print res1
        print res2  # todo add assertions

    def test_create_oncotree_diagnosis_query(self):

        q1 = self.q.create_oncotree_diagnosis_query(cancer_type='Lung', include=True)
        q2 = self.q.create_oncotree_diagnosis_query(cancer_type='Lung', include=False)
        res1 = self._find(q1)
        res2 = self._find(q2)

        assert res1 is not None
        assert res2 is not None
        assert res1[kn.sample_id_col] == 'TEST-SAMPLE-LUNG', res1
        assert res2[kn.sample_id_col] == 'TEST-SAMPLE-COLON', res2

    def test_create_age_query(self):
        raise NotImplementedError

    def test_create_gene_level_query(self):

        q1 = self.q.create_gene_level_query(gene_name='PTPN14', include=True)
        q2 = self.q.create_gene_level_query(gene_name='PTPN14', include=False)
        assert q1 == {
            kn.mutation_list_col: {
                '$elemMatch': {
                    kn.hugo_symbol_col: {'$eq': 'PTPN14'}
                }
            }
        }, q1
        assert q2 == {
            kn.mutation_list_col: {
                '$elemMatch': {
                    kn.hugo_symbol_col: {'$ne': 'PTPN14'}
                }
            }
        }, q2
