from src.utilities import settings as s
from src.data_store import key_names as kn
from src.data_store.data_model import mutations_schema, cnvs_schema, svs_schema


class VariantsUtilities:

    def __init__(self):
        self.col_dict = {
            s.variant_category_mutation_val: mutations_schema.keys(),
            s.variant_category_cnv_val: cnvs_schema.keys(),
            s.variant_category_sv_val: svs_schema.keys()
        }

    def create_variant_object(self, data, variant_type):
        """
        Create a mutation object from the given data

        :param data: {dict}
        :param variant_type: {str} (MUTATION, CNV, SV)
        :return: {dict}
        """
        variant_dict = {}
        for col in self.col_dict[variant_type]:
            if col in data:
                variant_dict[col] = data[col]

        # add reference residue for mutations
        if variant_type == s.variant_category_mutation_val:
            variant_dict[kn.ref_residue_col] = self._determine_reference_residue(data)

        return variant_dict

    @staticmethod
    def _determine_reference_residue(data):
        """
        Pull reference residue from protein change for all missense mutations

        :param data: {dict}
        :return: {str}
        """
        if data[kn.variant_class_col] == s.variant_class_missense_mutation_val:

            if kn.protein_change_col not in data or data[kn.protein_change_col] is None:
                raise ValueError('%s column must be set for all missense mutations' % kn.protein_change_col)

            return data[kn.protein_change_col][:-1]

    def determine_signature_type(self, data, sample_obj):
        """
        Determine signature type from the data

        :param data: {dict}
        :param sample_obj: {dict} This becomes the sample record in MongoDB
        :return: {dict} Updated sample object
        """

        cols_to_assess = s.signature_cols[:]
        cols_to_assess.remove(kn.ms_status_col)
        for col in cols_to_assess:
            if col == kn.mmr_status_col:
                sample_obj[kn.mmr_status_col], sample_obj[kn.ms_status_col] = self._split_mmr_status(data[col])
            elif col in data:
                sample_obj[col] = data[col]
            else:
                sample_obj[col] = None

        return sample_obj

    @staticmethod
    def _split_mmr_status(mmr_and_ms_status_text):
        """
        Split CAMD MMR Status text into MS Status and MMR Status

        :param mmr_and_ms_status_text: {str}
        :return: {tuple} MMR Status, MS Status
        """
        if mmr_and_ms_status_text is None:
            return None, None

        split_text = mmr_and_ms_status_text.split('(')
        mmr_status = split_text[0].strip()
        if mmr_status in [s.mmr_status_proficient_val, s.mmr_status_deficient_val]:
            ms_status = split_text[1].split('/')[1].split(')')[0].strip()
        else:
            ms_status = mmr_and_ms_status_text
            mmr_status = mmr_and_ms_status_text

        return mmr_status, ms_status

    @staticmethod
    def determine_wildtype(data, wt_gene_list):
        """
        Append wild type genes to the wild type gene list

        :param data: {dict}
        :param wt_gene_list: {list of str}
        :return: {list of str} Updated wt_gene_list
        """
        if kn.hugo_symbol_col not in data:
            raise ValueError('%s column must be included for wild type genes' % kn.hugo_symbol_col)

        return wt_gene_list.append(data[kn.hugo_symbol_col])
