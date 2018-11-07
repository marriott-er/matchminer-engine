from src.services.match_service.match_utils.shared_utils import SharedUtils
from src.services.match_service.match_utils.trial_utils import TrialUtils
from src.services.match_service.match_utils.trial_match_utils import TrialMatchUtils


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

            # crate mongo query from match tree
            matchengine.create_mongo_query_from_match_tree()

            # find matching records
            trial_matches = matchengine.search_for_matching_records()

            # sort trial matches
            trial_match_utils = TrialMatchUtils(trial_matches=trial_matches)
            trial_matches_df = trial_match_utils.sort_trial_matches()

            # save results
            utils.add_trial_matches(trial_matches_df=trial_matches_df)
