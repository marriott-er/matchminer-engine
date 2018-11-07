from src.utilities import settings as s
from tests.test_match_service import TestQueryUtilitiesShared
from src.services.match_service.match_utilities.shared_utilities import SharedUtilities


class TestSharedUtilities(TestQueryUtilitiesShared):

    def setUp(self):
        super(TestSharedUtilities, self).setUp()

        self.s = SharedUtilities()
        self.db.trial.drop()
        self.db.trial_match.drop()

    def tearDown(self):
        self.db.trial.drop()
        self.db.trial_match.drop()

    def test_find_trials(self):

        self.add_test_trials()
        res1 = self.s.find_trials()
        assert len(res1) == 7, len(res1)
        assert sorted(res1[0].keys()) == sorted([s.trial_protocol_no_col, s.trial_nct_id_col,
                                                 s.trial_treatment_list_col]), sorted(res1[0].keys())

        res2 = self.s.find_trials(query={s.trial_protocol_no_col: '00-002'})
        assert len(res2) == 1, len(res2)
        assert res2[0][s.trial_protocol_no_col] == '00-002', res2[0][s.trial_protocol_no_col]

    def test_add_trial_matches(self):

        self.add_test_trial_matches()
        self.s.add_trial_matches(trial_matches_df=self.trial_match_df)
        assert self._find(query={}, table='trial_match') is not None
