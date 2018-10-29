from src.utilities import settings as s


class QueryUtilities:

    def __init__(self):
        self.inclusion_dict = {True: '$eq', False: '$ne'}

    def create_oncotree_diagnosis_query(self, cancer_type, include=True):
        """
        Create MongoDB query to find records by oncotree diagnosis name

        :param cancer_type {str}
        :param include: {bool}
        :return: {dict}
        """
        # todo expand oncotree diagnosis
        return {s.diagnosis_col: {self.inclusion_dict[include]: cancer_type}}

    def create_age_query(self, include=True):
        """
        Create MongoDB query to find records by birth date

        :param include: {bool}
        :return: {dict}
        """
        raise NotImplementedError

    def create_gene_level_query(self, gene_name, variant_category, include=True):
        """
        Create MongoDB query to find records by gene name and variant category

        :param gene_name: {str}
        :param variant_category: {str}
        :param include: {bool}
        :return: {dict}
        """
        key = '{root}.{variant_category}.{gene_name}.{col}'.format(root=s.variants_key,
                                                                   variant_category=s.snv_key,
                                                                   gene_name=gene_name,
                                                                   col=s.variant_category_col)

        return {key: {self.inclusion_dict[include]: variant_category}}

    def create_variant_level_snv_missense_query(self, gene_name, protein_change, include=True):
        """
        Create MongoDB query to find SNV records by gene name and protein change

        :param gene_name: {str}
        :param protein_change: {str}
        :param include: {bool}
        :return: {dict}
        """
        key = '{root}.{variant_category}.{gene_name}.{col}'.format(root=s.variants_key,
                                                                   variant_category=s.snv_key,
                                                                   gene_name=gene_name,
                                                                   col=s.protein_change_col)

        return {key: {self.inclusion_dict[include]: protein_change}}

    def create_variant_level_cnv_query(self, gene_name, cnv_call, include=True):
        """
        Create MongoDB query to find CNV records by gene name and cnv call

        :param gene_name: {str}
        :param cnv_call: {str}
        :param include: {bool}
        :return: {dict}
        """
        key = '{root}.{variant_category}.{gene_name}.{col}'.format(root=s.variants_key,
                                                                   variant_category=s.cnv_key,
                                                                   gene_name=gene_name,
                                                                   col=s.cnv_call_col)

        return {key: {self.inclusion_dict[include]: cnv_call}}

    def create_sv_query(self, gene_name, include=True):
        """
        Create MongoDB query to find SV records through a regex pattern matching search.
        NOTE: This will produce false positives, so results should be reviewed manually.

        :param gene_name: {str}
        :param include: {bool}
        :return: {dict}
        """
        key = '{root}.{variant_category}.{col}'.format(root=s.variants_key,
                                                       variant_category=s.sv_key,
                                                       col=s.sv_comment_col)

        return {key: {self.inclusion_dict[include]: {'$regex': gene_name}}}

    def create_mutational_signature_query(self, signature_type, signature_val, include=True):
        """
        Create MongoDB query to find mutational signature records

        :param signature_type: {str}
        :param signature_val: {str}
        :param include: {bool}
        :return: {dict}
        """
        key = '{root}.{variant_category}.{col}'.format(root=s.variants_key,
                                                       variant_category=s.signature_key,
                                                       col=signature_type)

        return {key: {self.inclusion_dict[include]: signature_val}}

    @staticmethod
    def create_wild_type_query(gene_name):
        """
        Create MongoDB query to detect wild type gene calls

        :param gene_name: {str}
        :param include: {bool}
        :return: {dict}
        """
        key = '%s.{variant_category}.%s' % (s.variants_key, gene_name)
        val = {'$exists': False}
        wt_query = {
            '$and': [
                {key.format(variant_category=s.snv_key): val},
                {key.format(variant_category=s.cnv_key): val}
            ]
        }
        return wt_query