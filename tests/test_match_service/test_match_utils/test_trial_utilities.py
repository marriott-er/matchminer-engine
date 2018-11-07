from src.utilities import settings as s
from tests.test_match_service import TestQueryUtilitiesShared
from src.services.match_service.match_utilities.trial_utilities import TrialUtilities


class TestTrialUtilities(TestQueryUtilitiesShared):

    def setUp(self):
        super(TestTrialUtilities, self).setUp()

    def tearDown(self):
        pass

    def test_parse_match_trees_from_trial(self):

        # open trial with one step-level match tree
        t = TrialUtilities(trial=self.load_trial('10-113'))
        match_trees = t.parse_match_trees_from_trial()
        assert t.accrual_status == s.match_accrual_status_open_val
        assert len(match_trees) == 1, len(match_trees)
        assert match_trees[0].trial_level == s.trial_step_col, match_trees[0].trial_level

        # closed trial with one arm-level match tree
        t = TrialUtilities(trial=self.load_trial('10-114'))
        match_trees = t.parse_match_trees_from_trial()
        assert t.accrual_status == s.match_accrual_status_closed_val
        assert len(match_trees) == 1, len(match_trees)
        assert match_trees[0].trial_level == s.trial_arm_col, match_trees[0].trial_level

        # unspecified accrual status trial with two dose-level match trees
        t = TrialUtilities(trial=self.load_trial('00-005'))
        match_trees = t.parse_match_trees_from_trial()
        assert t.accrual_status == s.match_accrual_status_open_val
        assert len(match_trees) == 2, len(match_trees)
        assert match_trees[0].trial_level == s.trial_dose_col, match_trees[0].trial_level