import networkx as nx

from src.utilities import settings as s
from tests.test_match_service import TestQueryUtilitiesShared
from src.services.match_service.match_utils.trial_utils import TrialUtils
from src.services.match_service.match_utils.matchengine.matchengine import MatchEngine


class TestMatchEngine(TestQueryUtilitiesShared):

    def setUp(self):
        super(TestMatchEngine, self).setUp()

    def tearDown(self):
        pass

    # def _set_up_matchengine(self, trial):
    #     trial = self.load_trial(trial=trial)
    #     t = TrialUtils(trial=trial)
    #     return t.parse_match_trees_from_trial()[0]

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

    def test_convert_match_tree_to_digraph(self):

        me = MatchEngine(match_tree=self.simple_mutation_match_tree, trial_level=s.trial_arm_col)
        me.convert_match_tree_to_digraph()
        assert me.match_tree_nx is not None
        assert me.match_tree_nx.node[1] == {'type': 'and'}
        assert me.match_tree_nx.node[2] == {'type': 'genomic', 'value': self.simple_mutation_match_tree['and'][0]['genomic']}
        assert me.match_tree_nx.node[3] == {'type': 'clinical', 'value': self.simple_mutation_match_tree['and'][1]['clinical']}

    def test_create_mongo_query_from_match_tree(self):
        pass

    def test_assess_clinical_node(self):
        pass

    def test_assess_genomic_node(self):
        pass

    def test_search_for_matching_records(self):
        pass
