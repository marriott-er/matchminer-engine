from tests.test_match_service import TestQueryUtilitiesShared
from src.services.match_service.match_utils.matchengine.matchengine import MatchEngine
from src.services.match_service.match_utils.trial_utils import TrialUtils


class TestMatchEngineUtils(TestQueryUtilitiesShared):

    def setUp(self):
        super(TestMatchEngineUtils, self).setUp()

    def tearDown(self):
        pass

    def test_proof_of_concept(self):

        trial = self.load_trial(trial='10-113')
        t = TrialUtils(trial=trial)
        match_trees = t.parse_match_trees_from_trial()
        match_tree = match_trees[0]
        print match_tree.match_tree
