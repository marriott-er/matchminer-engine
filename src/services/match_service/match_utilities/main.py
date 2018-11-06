from src.services.match_service.match_utilities.shared_utilities import SharedUtilities
from src.services.match_service.match_utilities.trial_utilities import TrialUtilities
from src.services.match_service.match_utilities.trial_match_utilities import TrialMatchUtilities


def main():

    utils = SharedUtilities()

    # parse input arguments
    trials = utils.find_trials()
    for trial in trials:

        # parse trial document for all match trees
        trial_utils = TrialUtilities(trial=trial)
        matchengines = trial_utils.parse_match_trees_from_trial()
        for matchengine in matchengines:

            # create match tree
            matchengine.convert_match_tree_to_digraph()

            # crate mongo query from match tree

            # find matching records

            # sort trial matches
            trial_match_utils = TrialMatchUtilities(trial_matches=trial_matches)
            trial_matches_df = trial_match_utils.sort_trial_matches()

            # save results
            utils.add_trial_matches(trial_matches_df=trial_matches_df)

