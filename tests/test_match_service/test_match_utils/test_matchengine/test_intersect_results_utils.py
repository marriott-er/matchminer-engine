from src.utilities import settings as s
from src.data_store import key_names as kn
from tests.test_match_service import TestQueryUtilitiesShared
from src.services.match_service.match_utils.matchengine.intersect_results_utils import IntersectResultsUtils


class TestIntersectResultsUtils(TestQueryUtilitiesShared):

    def setUp(self):
        super(TestIntersectResultsUtils, self).setUp()

        self.i = IntersectResultsUtils()

    def tearDown(self):
        pass

    def test_get_sample_ids(self):
        pass

    def test_get_matches(self):
        pass

    def test_filter_matches(self):
        pass

    def test_update_old_match(self):
        pass

    def test_intersect_results(self):
        pass
