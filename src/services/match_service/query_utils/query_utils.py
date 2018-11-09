from src.utilities import settings as s
from src.data_store import key_names as kn


class QueryUtils(object):

    def __init__(self):
        self.list_inclusion_dict = {True: '$in', False: '$nin'}
        self.variant_category_dict = {
            s.variant_category_mutation_val: kn.mutation_list_col,
            s.variant_category_wildcard_mutation_val: kn.mutation_list_col,
            s.variant_category_exon_val: kn.mutation_list_col,
            s.variant_category_cnv_val: kn.cnv_list_col,
            s.variant_category_sv_val: kn.sv_list_col,
            s.variant_category_wt_val: kn.wt_genes_col
        }
        self.variant_type_col_dict = {
            s.variant_category_mutation_val: kn.protein_change_col,
            s.variant_category_wildcard_mutation_val: kn.ref_residue_col,
            s.variant_category_exon_val: kn.transcript_exon_col,
            s.variant_category_cnv_val: kn.cnv_call_col
        }

    @staticmethod
    def create_inclusion_query(variant_category, key, val):
        """
        Create MongoDB query that inclusively matches the given data

        :param variant_category: {str}
        :param key: {str}
        :param val: {any type}
        :return: {dict}
        """
        # todo unit test
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
        # todo unit test
        return {
            '$or': [
                {variant_category: {'$not': {'$elemMatch': {key: val}}}},
                {variant_category: []},
                {variant_category: {'$exists': False}}
            ]
        }
