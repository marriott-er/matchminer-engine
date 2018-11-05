from src.utilities import settings as s
from src.data_store import key_names as kn


from src.services.match_service.query_utilities.query_utilities import QueryUtilities
from src.services.match_service.query_utilities.genomic_utilities import GenomicUtilities


class GenomicQueries(QueryUtilities, GenomicUtilities):

    def __init__(self):
        QueryUtilities.__init__(self)
        GenomicUtilities.__init__(self)

    def create_gene_level_query(self, gene_name, include=True):
        """
        Create MongoDB query to find records by gene name and variant category

        :param gene_name: {str}
        :param include: {bool}
        :return: {dict}
        """
        query = {
            kn.mutation_list_col: {
                '$elemMatch': {
                    kn.hugo_symbol_col: {self.inclusion_dict[include]: gene_name}
                }
            }
        }
        return self.handle_exclusion_queries(query=query,
                                             variant_category=s.variant_category_mutation_val,
                                             include=include)

    def create_variant_level_snv_missense_query(self, gene_name, protein_change, include=True):
        """
        Create MongoDB query to find SNV records by gene name and protein change

        :param gene_name: {str}
        :param protein_change: {str}
        :param include: {bool}
        :return: {dict}
        """
        query = {
            kn.mutation_list_col: {
                '$elemMatch': {
                    kn.hugo_symbol_col: {self.inclusion_dict[include]: gene_name}
                }
            }
        }
        raise NotImplementedError
