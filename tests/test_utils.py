import string
import random
import unittest
from pymongo.mongo_client import ConnectionFailure

from src.utilities import settings as s
s.MONGO_URI = 'mongodb://localhost:27017'
s.MONGO_DBNAME = 'matchminer'

from src.utilities.utilities import *


class TestUtils(unittest.TestCase):

    def setUp(self):
        super(TestUtils, self).setUp()
        self.db = get_db(mongo_uri=s.MONGO_URI, mongo_dbname=s.MONGO_DBNAME)

    def tearDown(self):
        self.db.testCollection.drop()

    def test_get_db(self):

        connection_failure_1 = False
        connection_failure_2 = False
        try:
            get_db(mongo_uri='bad_uri', mongo_dbname=s.MONGO_DBNAME)
        except ConnectionFailure as e:
            connection_failure_1 = True

        try:
            get_db(mongo_uri=s.MONGO_URI, mongo_dbname=s.MONGO_DBNAME)
        except ConnectionFailure as e:
            connection_failure_2 = True

        assert connection_failure_1 is True
        assert connection_failure_2 is False

    def test_dataframe_to_json(self):

        data = [
            ['one', 'two', 'three'],
            ['four', 'five', 'six']
        ]
        cols = ['ONE', 'TWO', 'THREE']
        df = pd.DataFrame(data, columns=cols)
        res = dataframe_to_json(df)
        assert type(res) == list
        assert len(res) == 2
        assert res == [{'THREE': 'three', 'TWO': 'two', 'ONE': 'one'}, {'THREE': 'six', 'TWO': 'five', 'ONE': 'four'}]

    def test_handle_ints(self):

        assert handle_ints(col=kn.low_coverage_exon_col, val='1') == 1
        assert handle_ints(col=kn.low_coverage_exon_col, val=None) is None
        assert handle_ints(col=kn.show_codon_col, val=True) == True
        assert handle_ints(col=kn.show_codon_col, val=None) is None

    def test_handle_chromosome_column(self):

        assert handle_chromosome_column('1') == '1'
        assert handle_chromosome_column('1.0') == '1'
        assert handle_chromosome_column('X.0') == 'X.0'
        assert handle_chromosome_column('X') == 'X'

    def test_handle_vc(self):

        assert handle_vc(s.variant_category_mutation_val) == s.variant_category_mutation_val
        assert handle_vc('WT') == s.variant_category_wt_val

    def test_get_coordinating_center(self):

        t1 = {}
        assert get_coordinating_center(t1) == 'unknown'

        t2 = {s.trial_summary_col: {}}
        assert get_coordinating_center(t2) == 'unknown'

        t3 = {s.trial_summary_col: {s.trial_coordinating_center_col: 'DFCI'}}
        assert get_coordinating_center(t3) == 'DFCI'

    def test_chunk_table(self):

        docs = [
            {'test': ''.join([random.choice(string.ascii_letters).lower() for _ in range(10)])}
            for _ in range(100010)
        ]
        self.db.testCollection.insert(docs)
        df = load_table_in_chunks(db=self.db, table_name='testCollection')
        assert len(df.index) == 100010

    def test_set_dtypes(self):

        dtype_dict = {'stringCol': str, 'intCol': int, 'floatCol': float}

        cols = ['stringCol', 'intCol', 'floatCol']
        data = [[1.0, 1.0, '1'], [None, None, None]]
        df = pd.DataFrame(data, columns=cols)
        df = set_dtypes(df=df, dtype_dict=dtype_dict)
        assert type(df['stringCol'].tolist()[0]) == str
        assert type(df['intCol'].tolist()[0]) == int
        assert type(df['floatCol'].tolist()[0]) == float
        assert type(df['stringCol'].tolist()[1]) is None
        assert type(df['intCol'].tolist()[1]) is None
        assert type(df['floatCol'].tolist()[1]) is None

