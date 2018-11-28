import json
import logging
import pandas as pd
from pymongo import MongoClient

from src.utilities import settings as s
from src.data_store import key_names as kn
from src.utilities.settings import MONGO_URI, MONGO_DBNAME

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s', )


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


def chunk_table(db, table_name, df=None, chunk=0):
    """
    Create a Pandas dataframe in chunks

    :param db: {MongoDB connection}
    :param table_name: {str}
    :param df: {Pandas dataframe}
    :param chunk: {int}
    :return: {Pandas dataframe}
    """
    chunk_size = 10000
    num_records = db[table_name].count()
    if df is None:
        df = pd.DataFrame()

    while chunk < num_records:
        if df is not None:
            logging.info('Loaded %d records into Pandas' % len(df.index))
        cursor = db[table_name].find().sort([("$natural", 1)]).skip(chunk).limit(chunk_size)
        df = df.append(pd.DataFrame.from_records(cursor))
        chunk += chunk_size

    return df
