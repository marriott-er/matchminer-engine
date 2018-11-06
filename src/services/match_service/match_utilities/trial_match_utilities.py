import logging

from src.services.match_service.match_utilities.sort import add_sort_order

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s', )


class TrialMatchUtilities:

    def __init__(self, trial_matches):
        self.trial_matches = trial_matches

    def sort_trial_matches(self):
        """
        Sort trial matches.

        :return: {Pandas dataframe}
        """

        logging.info('Sorting trial matches')
        return add_sort_order(self.trial_matches)
