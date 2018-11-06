from src.utilities import settings as s
from src.data_store import key_names as kn


class QueryUtilities(object):

    def __init__(self):
        self.inclusion_dict = {True: '$eq', False: '$ne'}
        self.list_inclusion_dict = {True: '$in', False: '$nin'}
        self.variant_category_dict = {
            s.variant_category_mutation_val: kn.mutation_list_col,
            s.variant_category_cnv_val: kn.cnv_list_col,
            s.variant_category_sv_val: kn.sv_list_col,
            s.variant_category_wt_val: kn.wt_genes_col
        }
        self.variant_type_col_dict = {
            s.variant_category_mutation_val: kn.protein_change_col,
            s.variant_category_wildcard_mutation_val: kn.ref_residue_col,
            s.variant_category_cnv_val: kn.cnv_call_col
        }

    def handle_exclusion_queries(self, query, variant_category, include):
        """
        Update MongoDB query with additional parameters if it is an exclusion criteria

        :param query: {dict}
        :param variant_category: {str} (MUTATION, CNV, SV)
        :param include: {bool}
        :return: {dict}
        """
        if include:
            return query
        else:
            return {'$or': [query, self.create_no_variants_query(variant_category=variant_category)]}

    def create_no_variants_query(self, variant_category):
        """
        Create MongoDB query that matches samples without any variants in the specified variant category.

        :param variant_category: {str} (MUTATION, CNV, SV, WT)
        :return: {dict}
        """
        return {
            '$or': [
                {self.variant_category_dict[variant_category]: []},
                {self.variant_category_dict[variant_category]: {'$exists': False}}
            ]
        }
