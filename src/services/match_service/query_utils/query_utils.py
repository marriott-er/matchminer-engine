from src.utilities import settings as s
from src.data_store import key_names as kn


class QueryUtils(object):

    def __init__(self):
        self.list_inclusion_dict = {True: '$in', False: '$nin'}

    @staticmethod
    def create_inclusion_query(variant_category, key, val):
        """
        Create MongoDB query that inclusively matches the given data

        :param variant_category: {str}
        :param key: {str}
        :param val: {any type}
        :return: {dict}
        """
        return {variant_category: {'$elemMatch': {key: val}}}

    @staticmethod
    def create_exclusion_query(variant_category, key, val):
        """
        Create MongoDB query that exclusively matches the given data

        :param variant_category: {str}
        :param key: {str}
        :param val: {any type}
        :return: {dict}
        """
        return {
            '$or': [
                {variant_category: {'$not': {'$elemMatch': {key: val}}}},
                {variant_category: []},
                {variant_category: {'$exists': False}}
            ]
        }
