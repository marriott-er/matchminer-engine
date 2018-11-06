import re

from src.utilities import settings as s
from src.data_store import key_names as kn
from src.services.match_service.query_utilities.query_utilities import QueryUtilities
from src.services.match_service.query_utilities.genomic_utilities import GenomicUtilities


class GenomicQueries(QueryUtilities, GenomicUtilities):

    def __init__(self):
        QueryUtilities.__init__(self)
        GenomicUtilities.__init__(self)

    def create_gene_level_query(self, gene_name, variant_category, include=True):
        """
        Create MongoDB query to find records by gene name and variant category

        :param gene_name: {str}
        :param variant_category: {str} (MUTATION, CNV, SV, WT)
        :param include: {bool}
        :return: {dict}
        """
        query = {
            self.variant_category_dict[variant_category]: {
                '$elemMatch': {
                    kn.hugo_symbol_col: {self.inclusion_dict[include]: gene_name}
                }
            }
        }
        return self.handle_exclusion_queries(query=query,
                                             variant_category=variant_category,
                                             include=include)

    def create_variant_level_snv_missense_query(self, gene_name, protein_change, include=True):
        """
        Create MongoDB query to find SNV records by gene name and protein change

        :param gene_name: {str}
        :param protein_change: {str}
        :param include: {bool}
        :return: {dict}
        """
        if include:
            query = {
                kn.mutation_list_col: {
                    '$elemMatch': {
                        kn.hugo_symbol_col: {'$eq': gene_name},
                        kn.protein_change_col: {'$eq': protein_change}
                    }
                }
            }
        else:
            exclude_query = {
                kn.mutation_list_col: {
                    '$elemMatch': {
                        kn.hugo_symbol_col: {'$eq': gene_name},
                        kn.protein_change_col: {'$ne': protein_change}
                    }
                }
            }
            query = {'$or': [
                self.create_gene_level_query(gene_name=gene_name,
                                             variant_category=s.variant_category_mutation_val,
                                             include=False),
                exclude_query
            ]}

        return query

    def create_cnv_query(self, gene_name, cnv_call, include=True):
        """
        Create MongoDB query to find CNV records by gene name and, if supplied, cnv call

        :param gene_name: {str}
        :param cnv_call: {str}
        :param include: {bool}
        :return: {dict}
        """
        if include:
            query = {
                kn.cnv_list_col: {
                    '$elemMatch': {
                        kn.hugo_symbol_col: {'$eq': gene_name},
                        kn.cnv_call_col: {'$eq': cnv_call}
                    }
                }
            }
        else:
            exclude_query = {
                kn.cnv_list_col: {
                    '$elemMatch': {
                        kn.hugo_symbol_col: {'$eq': gene_name},
                        kn.cnv_call_col: {'$ne': cnv_call}
                    }
                }
            }
            query = {'$or': [
                self.create_gene_level_query(gene_name=gene_name,
                                             variant_category=s.variant_category_cnv_val,
                                             include=False),
                exclude_query
            ]}

        return query

    def create_sv_query(self, gene_name, include=True):
        """
        Create MongoDB query to find SV records by regex string matching of the given gene name
        to a free text structrual variant comment field.

        :param gene_name: {str}
        :param include: {bool}
        :return: {dict}
        """
        gene_name_regex = self.regex_compile_gene_name(gene_name)
        if include:
            subquery = {kn.sv_comment_col: gene_name_regex}
        else:
            subquery = {kn.sv_comment_col: {'$not': gene_name_regex}}

        query = {kn.sv_list_col: {'$elemMatch': subquery}}
        return self.handle_exclusion_queries(query=query, variant_category=s.variant_category_sv_val, include=include)

    def create_mutational_signature_query(self, signature_type, signature_val, include=True):
        """
        Create MongoDB query to find records by the given mutational signature value.

        :param signature_type: {str} (e.g. MMR Status, TMZ Status, etc.)
        :param signature_val: {str}
        :param include: {bool}
        :return: {dict}
        """
        return {signature_type: {self.inclusion_dict[include]: signature_val}}

    def create_wildcard_query(self, gene_name, protein_change, include=True):
        """
        Create MongoDB query to find samples that match the given wildcard protein change value

        :param gene_name: {str}
        :param protein_change: {str}
        :param include: {bool}
        :return: {dict}
        """
        raise NotImplementedError

    def create_exon_query(self, gene_name, exon, include=True):
        """
        Create MongoDB query to find samples with mutations in the given exon.

        :param gene_name: {str}
        :param exon: {int}
        :param include: {bool}
        :return: {dict}
        """
        raise NotImplementedError

    def create_low_coverage_query(self, gene_name, low_coverage_type, include=True):
        """
        Create MongoDB query to find samples with genes identified as low coverage.

        :param gene_name: {str}
        :param low_coverage_type: {str} (e.g. Pertinent Low Coverage, Additional Low Coverage)
        :param include: {bool}
        :return: {dict}
        """
        raise NotImplementedError
