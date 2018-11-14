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

        node = {'matches': [
            {kn.sample_id_col: 'DEV1'},
            {kn.sample_id_col: 'DEV2'}
        ]}
        res = self.i._get_sample_ids(node)
        assert sorted(res) == ['DEV1', 'DEV2'], res

    def test_filter_matches(self):

        sample_ids = ['DEV1', 'DEV3']
        node = {'matches': [
            {kn.sample_id_col: 'DEV1'},
            {kn.sample_id_col: 'DEV2'}
        ]}
        res = self.i._filter_matches(node=node, sample_ids=sample_ids)
        assert sorted(res) == ['DEV1'], res

    def test_update_old_match(self):

        keys = ['key1', 'key2']
        old_match = {'key0': 0}
        child_match = {'key1': 1}
        res = self.i._update_old_match(old_match, child_match, keys)
        assert res == {'key0': 0, 'key1': 1}, res

        old_match = {'key1': 1}
        child_match = {'key1': 1}
        res = self.i._update_old_match(old_match, child_match, keys)
        assert res == {'key1': 1}, res

        old_match = {'key1': {'one': 1}}
        child_match = {'key1': {'two': 2}}
        res = self.i._update_old_match(old_match, child_match, keys, genomic=True)
        assert res == {'key1': [{'one': 1}, {'two': 2}]}, res

    def test_intersect_results(self):
        pass
