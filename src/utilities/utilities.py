import json
import logging
from pymongo import MongoClient

from src.utilities import settings as s
from src.data_store import key_names as kn
from src.utilities.settings import MONGO_URI, MONGO_DBNAME

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s', )

# todo unit test this entire file

def get_db(mongo_uri=MONGO_URI, mongo_dbname=MONGO_DBNAME):
    """Returns a Mongo connection"""
    connection = MongoClient(mongo_uri)
    return connection[mongo_dbname]


def dataframe_to_json(df):
    """Converts Pandas dataframe to json object"""
    return json.loads(df.to_json(orient='records'))


def handle_ints(col, val):
    """
    Convert integer column values to type integer

    :param col: {str} Column name
    :parm val: {None, float} Column value
    :return: {int}
    """
    gint_cols = [
        kn.low_coverage_exon_col,
        kn.transcript_exon_col,
        kn.position_col,
        kn.codon_col,
        kn.tier_col,
        kn.cnv_row_id_col
    ]
    if col in gint_cols and val:
        return int(val)
    else:
        return val


def handle_chromosome_column(val):
    """
    Ensure chromosome column values are stored as strings without trailing decimal places

    :param val: {str}
    :return: {str}
    """
    if val.split('.')[0].isdigit():
        return val.split('.')[0]
    else:
        return val


def get_coordinating_center(trial):
    """
    Returns the trials' coordinating center

    :param trial: {dict}
    :return: {str}
    """

    if s.trial_summary_col not in trial or s.trial_coordinating_center_col not in trial[s.trial_summary_col]:
        return 'unknown'
    else:
        return trial[s.trial_summary_col][s.trial_coordinating_center_col]
