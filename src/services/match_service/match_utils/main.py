import logging

from src.services.match_service.match_utils.shared_utils import SharedUtils
from src.services.match_service.match_utils.trial_utils import TrialUtils
from src.services.match_service.match_utils.trial_match_utils import TrialMatchUtils

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s', )


def main():

    utils = SharedUtils()

    # parse input arguments
    trials = utils.find_trials()
    for trial in trials:

        # parse trial document for all match trees
        trial_utils = TrialUtils(trial=trial)
        matchengines = trial_utils.parse_match_trees_from_trial()
        for matchengine in matchengines:

            # create match tree
            matchengine.convert_match_tree_to_digraph()

            # crate mongo query from match tree and find matching records
            matchengine.traverse_match_tree()

            # create trial matches records
            trial_match_utils = TrialMatchUtils(matched_samples=matchengine.matched_samples)
            trial_match_utils.create_trial_match_records()
            trial_matches_df = trial_match_utils.sort_trial_matches()

            # save results
            utils.add_trial_matches(trial_matches_df=trial_matches_df)

    logging.info('DONE')
