import logging

from src.utilities import settings as s
from src.services.match_service.match_utilities.matchengine import MatchEngine

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s', )


class TrialUtilities:

    def __init__(self, trial):
        self.trial = trial
        self.accrual_status = s.match_accrual_status_open_val

    def parse_match_trees_from_trial(self):
        """
        Iterates through all match clauses of the given trial.

        :return: {list of MatchEngine class objects} Each item is a MatchEngine object instantiated with a match tree
        """
        # todo unit test
        logging.info('Matching trial %s' % self.trial[s.trial_protocol_no_col])

        # If the trial is not open to accrual, all matches to all match trees in this trial will be marked closed
        if s.trial_summary_col in self.trial:

            trial_summary = self.trial[s.trial_summary_col]
            if s.trial_accrual_status_col in trial_summary:
                trial_status = trial_summary[s.trial_accrual_status_col]

                if isinstance(trial_status, list) and 'value' in trial_status[0]:
                    if trial_status[0]['value'].lower() != s.trial_accrual_status_open_val:
                        self.accrual_status = s.match_accrual_status_closed_val

        # match trees can be pulled from step, arm or dose levels
        match_trees = []

        # STEP #
        for step in self.trial[s.trial_treatment_list_col][s.trial_step_col]:
            if s.trial_match_tree_col in step:
                matchengine = MatchEngine(match_tree=step[s.trial_match_tree_col], trial_level=s.trial_step_col)
                match_trees.append(matchengine)

            # ARM #
            for arm in step[s.trial_arm_col]:
                if s.trial_match_tree_col in arm:
                    matchengine = MatchEngine(match_tree=arm[s.trial_match_tree_col], trial_level=s.trial_arm_col)
                    match_trees.append(matchengine)

                # DOSE #
                for dose in arm[s.trial_dose_col]:
                    if s.trial_match_tree_col in dose:
                        matchengine = MatchEngine(match_tree=dose[s.trial_match_tree_col], trial_level=s.trial_dose_col)
                        match_trees.append(matchengine)

        return match_trees
