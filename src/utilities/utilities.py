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


def map_variant_category_name_to_data_model(val):
    """
    Map the string text value for the genomic column "variantCategory" to
    the corresponding key name in the samples data model.

    :param val: {str}
    :return: {str}
    """
    variant_category_dict = {
        'MUTATION': 'snvs',
        'CNV': 'cnvs',
        'SV': 'svs',
        'SIGNATURE': 'signatures'
    }
    return variant_category_dict[val]
