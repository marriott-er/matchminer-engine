from src.utilities import settings as s


class VariantsUtilities:

    def __init__(self):
        self.col_dict = {
            s.variant_category_mutation_val: s.mutation_cols,
            s.variant_category_cnv_val: s.cnv_cols,
            s.variant_category_sv_val: s.sv_cols
        }

    def create_variant_object(self, data, variant_type):
        """
        Create a mutation object from the given old_data

        :param data: {list of mixed type}
        :param variant_type: {str} (MUTATION, CNV, SV)
        :return: {dict}
        """
        variant_dict = {}
        for col in self.col_dict[variant_type]:
            if col in data:
                variant_dict[col] = data[col]

        return variant_dict

    def determine_reference_residue(self, protein_change):
        """
        TODO
        :param protein_change:
        :return:
        """
        raise NotImplementedError

    def determine_signature_type(self, data):
        """
        Determine signature type from the old_data

        :param data: {list of mixed type}
        :return: {str}
        """
        raise NotImplementedError

    def split_mmr_status(self, mmr_status):
        """
        Split CAMD MMR Status text into MS Status and MMR Status

        :param mmr_status: {str}
        :return: {tuple}
        """
        raise NotImplementedError


    # todo add pertinent negatives