import re

from src.data_store import key_names as kn


class GenomicUtils:

    def __init__(self):

        self.hugo_symbol_key = kn.hugo_symbol_col
        self.protein_change_key = kn.protein_change_col
        self.ref_residue_key = kn.ref_residue_col
        self.transcript_exon_key = kn.transcript_exon_col
        self.cnv_call_key = kn.cnv_call_col
        self.variant_class_key = kn.variant_class_col
        self.sv_comment_key = kn.sv_comment_col

    @staticmethod
    def regex_compile_gene_name(gene_name):
        """
        Converts the gene name into a compiled regex object

        :param gene_name: {str}
        :return: {regex object}
        """
        return re.compile("(.*\W{0}\W.*)|(^{0}\W.*)|(.*\W{0}$)".format(gene_name), re.IGNORECASE)
