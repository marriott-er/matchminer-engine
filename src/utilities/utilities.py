import json
import logging
from pymongo import MongoClient

from src.utilities.settings import MONGO_URI, MONGO_DBNAME

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s', )


def get_db(mongo_uri=MONGO_URI, mongo_dbname=MONGO_DBNAME):
    """Returns a Mongo connection"""
    connection = MongoClient(mongo_uri)
    return connection[mongo_dbname]


def dataframe_to_json(df):
    """Converts Pandas dataframe to json object"""
    return json.loads(df.T.to_json()).values()
