from src.utilities import settings as s
from tests.test_match_service import TestQueryUtilitiesShared
from src.services.match_service.match_utils.trial_utils import TrialUtils


class TestTrialUtils(TestQueryUtilitiesShared):

    def setUp(self):
        super(TestTrialUtils, self).setUp()

    def tearDown(self):
        pass

    def test_parse_match_trees_from_trial(self):

        # open trial with one step-level match tree
        t = TrialUtils(trial=self.load_trial('10-113'))
        match_trees = t.parse_match_trees_from_trial()
        assert t.accrual_status == s.match_accrual_status_open_val
        assert len(match_trees) == 1, len(match_trees)
        assert match_trees[0].trial_info['protocol_no'] == '10-113'
        assert match_trees[0].trial_info['accrual_status'] == s.match_accrual_status_open_val
        assert match_trees[0].trial_info['level'] == s.trial_step_col
        assert match_trees[0].trial_info['step_code'] == '1'
        assert match_trees[0].trial_info['arm_code'] is None
        assert match_trees[0].trial_info['dose_code'] is None

        # closed trial with one arm-level match tree
        t = TrialUtils(trial=self.load_trial('10-114'))
        match_trees = t.parse_match_trees_from_trial()
        assert t.accrual_status == s.match_accrual_status_closed_val
        assert len(match_trees) == 1, len(match_trees)
        assert match_trees[0].trial_info['protocol_no'] == '10-114'
        assert match_trees[0].trial_info['accrual_status'] == s.match_accrual_status_closed_val
        assert match_trees[0].trial_info['level'] == s.trial_arm_col
        assert match_trees[0].trial_info['step_code'] == '1'
        assert match_trees[0].trial_info['arm_code'] == '1'
        assert match_trees[0].trial_info['dose_code'] is None

        # unspecified accrual status trial with two dose-level match trees
        t = TrialUtils(trial=self.load_trial('00-005'))
        match_trees = t.parse_match_trees_from_trial()
        assert t.accrual_status == s.match_accrual_status_open_val
        assert len(match_trees) == 2, len(match_trees)
        assert match_trees[0].trial_info['protocol_no'] == '00-005'
        assert match_trees[0].trial_info['accrual_status'] == s.match_accrual_status_open_val
        assert match_trees[0].trial_info['level'] == s.trial_dose_col
        assert match_trees[0].trial_info['step_code'] == '1'
        assert match_trees[0].trial_info['arm_code'] == 'DOSE'
        assert match_trees[0].trial_info['dose_code'] == '1'
