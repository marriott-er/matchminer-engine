from src.utilities import settings as s
from src.data_store import key_names as kn
from src.utilities.utilities import handle_ints
from src.data_store.data_model import mutations_schema, cnvs_schema, svs_schema, low_coverage_schema


class VariantsUtilities:

    def __init__(self, sample_obj):
        self.sample_obj = sample_obj
        self.col_dict = {
            s.variant_category_mutation_val: mutations_schema.keys(),
            s.variant_category_cnv_val: cnvs_schema.keys(),
            s.variant_category_sv_val: svs_schema.keys()
        }

        # method calls by variant category
        self.variant_parser_dict = {
            s.variant_category_mutation_val: self.create_variant_object,
            s.variant_category_cnv_val: self.create_variant_object,
            s.variant_category_sv_val: self.create_variant_object,
            s.variant_category_signature_val: self.determine_signature_type,
            s.variant_category_wt_val: self.determine_wildtype,
            s.variant_category_lc_val: self.determine_low_coverage_type
        }
        self._init_sample_obj()

    def _init_sample_obj(self):
        """
        Initialize the sample object with genomic columns

        :return: {null}
        """

        # Initialize Mutations, CNVs, SVs, Wild-type genes, and Low-coverage genes to empty arrays
        for gcol in s.gcol_list:
            self.sample_obj[gcol] = []

        # Initialize all signature types to null
        for scol in s.signature_cols:
            self.sample_obj[scol] = None

    def create_variant_object(self, data):
        """
        Create a mutation object from the given data

        :param data: {dict}
        :return: {null}
        """
        variant_map = {
            s.variant_category_mutation_val: kn.mutation_list_col,
            s.variant_category_cnv_val: kn.cnv_list_col,
            s.variant_category_sv_val: kn.sv_list_col
        }
        variant_obj = {}
        variant_type = data[kn.variant_category_col]
        for col in self.col_dict[variant_type]:
            if col in data:
                variant_obj[col] = handle_ints(col=col, val=data[col])

        # add reference residue for mutations
        if variant_type == s.variant_category_mutation_val:
            variant_obj[kn.ref_residue_col] = self._determine_reference_residue(data)

        variant_col = variant_map[variant_type]
        self.sample_obj[variant_col].append(variant_obj)

    def determine_signature_type(self, data):
        """
        Determine signature type from the data

        :param data: {dict}
        :return: {null}
        """

        cols_to_assess = s.signature_cols[:]
        cols_to_assess.remove(kn.ms_status_col)
        for col in cols_to_assess:
            if col == kn.mmr_status_col:
                self.sample_obj[kn.mmr_status_col], self.sample_obj[kn.ms_status_col] = self._split_mmr_status(data[col])
            elif col in data:
                self.sample_obj[col] = data[col]
            else:
                self.sample_obj[col] = None

    def determine_wildtype(self, data):
        """
        Append wild type genes to the wild type gene list

        :param data: {dict}
        :return: {null}
        """
        if kn.hugo_symbol_col not in data:
            raise ValueError('%s column must be included for wild type genes' % kn.hugo_symbol_col)

        self.sample_obj[kn.wt_genes_col].append(data[kn.hugo_symbol_col])

    def determine_low_coverage_type(self, data):
        """
        Group low coverage gene objects by their type

        :param data: {dict}
        :return: {null}
        """
        lc_map = {
            s.pertinent_negative_val: kn.pertinent_negatives_list_col,
            s.pertinent_low_coverage_val: kn.pertinent_undercovered_list_col,
            s.additional_low_coverage_val: kn.additional_undercovered_list_col
        }

        if kn.coverage_type_col not in data.keys() or data[kn.coverage_type_col] not in lc_map.keys():
            raise ValueError('%s column must be included for low coverage genes' % kn.coverage_type_col)

        lc_obj = {}
        lc_cols = low_coverage_schema.keys()
        for col in lc_cols:
            if col in data:
                lc_obj[col] = handle_ints(col=col, val=data[col])

        coverage_type = data[kn.coverage_type_col]
        low_coverage_col = lc_map[coverage_type]
        self.sample_obj[low_coverage_col].append(lc_obj)

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
