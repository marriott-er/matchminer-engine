from src.utilities import settings as s
from src.data_store import key_names as kn
from tests.test_match_service import TestQueryUtilitiesShared
from src.services.match_service.match_utils.trial_utils import TrialUtils
from src.services.match_service.match_utils.matchengine.matchengine import MatchEngine


class TestMatchEngine(TestQueryUtilitiesShared):

    def setUp(self):
        super(TestMatchEngine, self).setUp()

        self.db.testSamples.insert_many(self.test_cases)

    # def tearDown(self):
    #     self.db.testSamples.drop()
    #     self.db[s.sample_collection_name].drop()

    @staticmethod
    def _set_up_matchengine(trial):
        t = TrialUtils(trial=trial)
        return t.parse_match_trees_from_trial()[0]

    def test_proof_of_concept(self):

        # todo NOTE: this isn't really a unit test

        trial = self.load_trial(trial='10-113')
        print trial
        t = TrialUtils(trial=trial)
        matchengines = t.parse_match_trees_from_trial()
        matchengine = matchengines[0]
        print 'match tree'
        self._print(matchengine.match_tree)

        matchengine.convert_match_tree_to_digraph()
        matchengine.create_mongo_query_from_match_tree()
        print
        print 'query'
        self._print(matchengine.query)

    def test_complex_conversion(self):
        pass

    def test_convert_match_tree_to_digraph(self):

        me = MatchEngine(match_tree=self.simple_mutation_match_tree, trial_info={})
        me.convert_match_tree_to_digraph()
        assert me.match_tree_nx is not None
        assert me.match_tree_nx.node[1] == {'type': 'and'}
        assert me.match_tree_nx.node[2] == {'type': 'genomic', 'value': self.simple_mutation_match_tree['and'][0]['genomic']}
        assert me.match_tree_nx.node[3] == {'type': 'clinical', 'value': self.simple_mutation_match_tree['and'][1]['clinical']}

    def test_create_mongo_query_from_match_tree(self):

        # oncotree diagnosis
        me = MatchEngine(match_tree=self.simple_mutation_match_tree, trial_info={})
        me.convert_match_tree_to_digraph()
        me.create_mongo_query_from_match_tree()
        res1 = self._findalls(me.query)
        self._print(me.query)
        assert len(res1) == 1, res1
        assert res1 == ['TEST-SAMPLE-BRAF-V600E'], res1
        assert False

        # all solid tumors expansion
        me = MatchEngine(match_tree=self.all_solid_tumor_match_tree, trial_info={})
        me.convert_match_tree_to_digraph()
        me.create_mongo_query_from_match_tree()
        res2 = self._findalls(me.query)
        # self._print(me.query)
        assert len(res2) == 1, res2
        assert res2 == ['TEST-SAMPLE-BRAF-V600E'], res2

        # gender
        me = MatchEngine(match_tree=self.all_male_match_tree, trial_info={})
        me.convert_match_tree_to_digraph()
        me.create_mongo_query_from_match_tree()
        res3 = self._findalls(me.query)
        # self._print(me.query)
        assert len(res3) == 1, res3
        assert res3 == ['TEST-SAMPLE-BRAF-V600E'], res3

        # gender and all liquid tumor expansion
        me = MatchEngine(match_tree=self.all_female_match_tree, trial_info={})
        me.convert_match_tree_to_digraph()
        me.create_mongo_query_from_match_tree()
        res4 = self._findalls(me.query)
        # self._print(me.query)
        assert len(res4) == 1, res4
        assert res4 == ['TEST-SAMPLE-BRAF-NON-V600E'], res4

        # pediatric cnv
        me = MatchEngine(match_tree=self.pediatric_cnv_match_tree, trial_info={})
        me.convert_match_tree_to_digraph()
        me.create_mongo_query_from_match_tree()
        res5 = self._findalls(me.query)
        # self._print(me.query)
        assert len(res5) == 1, res5
        assert res5 == ['TEST-SAMPLE-BRAF-CNV-HETERO-DEL'], res5

    def test_search_for_matching_records(self):

        self.db[s.sample_collection_name].insert_many(self.test_cases)
        me = MatchEngine(match_tree=self.pediatric_cnv_match_tree, trial_info={})
        me.convert_match_tree_to_digraph()
        me.create_mongo_query_from_match_tree()
        me.search_for_matching_records()
        # self._print(me.query)
        assert me.matched_samples == [{kn.sample_id_col: 'TEST-SAMPLE-BRAF-CNV-HETERO-DEL'}]
