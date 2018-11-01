import unittest

from tests.test_load_service import *
from src.data_store import data_model as dm
from src.services.load_service.variants_utilities import VariantsUtilities


class TestVariantsUtilities(unittest.TestCase):

    def setUp(self):
        super(TestVariantsUtilities, self).setUp()

        self.v = VariantsUtilities()

    def tearDown(self):
        pass

    def test_determine_reference_residue(self):

        ref_residue_missense = self.v._determine_reference_residue(data=mutation_missense_data)
        ref_residue_nonsense = self.v._determine_reference_residue(data=mutation_nonsense_data)

        assert ref_residue_missense == 'p.V600', ref_residue_missense
        assert ref_residue_nonsense is None, ref_residue_nonsense

        # catch missing data
        return_value_error = False
        missing_protein_change_data = mutation_missense_data.copy()
        del missing_protein_change_data[kn.protein_change_col]
        try:
            self.v._determine_reference_residue(data=missing_protein_change_data)
        except ValueError:
            return_value_error = True

        assert return_value_error is True

    def test_create_variant_object(self):

        mutation_dict = self.v.create_variant_object(data=mutation_missense_data,
                                                     variant_type=s.variant_category_mutation_val)
        cnv_dict = self.v.create_variant_object(data=cnv_heterozygous_del_data,
                                                variant_type=s.variant_category_cnv_val)
        sv_dict = self.v.create_variant_object(data=sv_data,
                                               variant_type=s.variant_category_sv_val)

        assert sorted(mutation_dict.keys()) == sorted(dm.mutations_schema.keys()), sorted(mutation_dict.keys())
        assert sorted(cnv_dict.keys()) == sorted(dm.cnvs_schema.keys()), sorted(cnv_dict.keys())
        assert sorted(sv_dict.keys()) == sorted(dm.svs_schema.keys()), sorted(sv_dict.keys())

    def test_split_mmr_status(self):

        unsupported_text = 'TEST'
        res1 = self.v._split_mmr_status(None)
        res2 = self.v._split_mmr_status(s.mmr_status_cannot_assess_val)
        res3 = self.v._split_mmr_status(s.mmr_status_indeterminate_val)
        res4 = self.v._split_mmr_status('Proficient (MMR-P / MSS)')
        res5 = self.v._split_mmr_status('Deficient (MMR-D / MSI-H)')
        res6 = self.v._split_mmr_status(unsupported_text)

        assert res1 == (None, None), res1
        assert res2 == (s.mmr_status_cannot_assess_val, s.mmr_status_cannot_assess_val), res2
        assert res3 == (s.mmr_status_indeterminate_val, s.mmr_status_indeterminate_val), res3
        assert res4 == (s.mmr_status_proficient_val, s.ms_status_mss_val), res4
        assert res5 == (s.mmr_status_deficient_val, s.ms_status_msih_val), res5
        assert res6 == (unsupported_text, unsupported_text), res6

    def test_determine_signature_type(self):

        # MMR deficient
        sample_obj = {}
        sample_obj = self.v.determine_signature_type(data=signature_mmr_deficient_data, sample_obj=sample_obj)
        assert sorted(sample_obj.keys()) == sorted(s.signature_cols), sorted(sample_obj.keys())
        assert sample_obj[kn.mmr_status_col] == s.mmr_status_deficient_val, sample_obj[kn.mmr_status_col]
        assert sample_obj[kn.ms_status_col] == s.ms_status_msih_val, sample_obj[kn.ms_status_col]
        assert sample_obj[kn.apobec_status_col] is None, sample_obj[kn.apobec_status_col]

        # MMR not specified
        sample_obj = {}
        sample_obj = self.v.determine_signature_type(data=signature_mmr_none_data, sample_obj=sample_obj)
        assert sorted(sample_obj.keys()) == sorted(s.signature_cols), sorted(sample_obj.keys())
        assert sample_obj[kn.mmr_status_col] is None, sample_obj[kn.mmr_status_col]
        assert sample_obj[kn.ms_status_col] is None, sample_obj[kn.ms_status_col]

    def test_determine_wildtype(self):

        wt_gene_list = []
        wt_gene_list = self.v.determine_wildtype(data=wt1_data, wt_gene_list=wt_gene_list)
        assert sorted(wt_gene_list) == sorted(['BRAF']), sorted(wt_gene_list)

        wt_gene_list = self.v.determine_wildtype(data=wt2_data, wt_gene_list=wt_gene_list)
        assert sorted(wt_gene_list) == sorted(['BRAF', 'EGFR']), sorted(wt_gene_list)

        # catch missing data
        return_value_error = False
        missing_protein_change_data = {}
        try:
            self.v.determine_wildtype(data=missing_protein_change_data, wt_gene_list=wt_gene_list)
        except ValueError:
            return_value_error = True

        assert return_value_error is True

    def test_determine_low_coverage_type(self):

        lcd = {
            kn.pertinent_negatives_list_col: [],
            kn.pertinent_undercovered_list_col: [],
            kn.additional_undercovered_list_col: []
        }

        # PN
        lcd = self.v.determine_low_coverage_type(data=pertinent_negative_data, low_coverage_dict=lcd)
        assert lcd[kn.pertinent_negatives_list_col] == [pertinent_negative_data], lcd[kn.pertinent_negatives_list_col]
        assert lcd[kn.pertinent_undercovered_list_col] == [], lcd[kn.pertinent_undercovered_list_col]
        assert lcd[kn.additional_undercovered_list_col] == [], lcd[kn.additional_undercovered_list_col]

        # PLC
        lcd = self.v.determine_low_coverage_type(data=pertinent_undercovered_data, low_coverage_dict=lcd)
        assert lcd[kn.pertinent_negatives_list_col] == [pertinent_negative_data], lcd[kn.pertinent_negatives_list_col]
        assert lcd[kn.pertinent_undercovered_list_col] == [pertinent_undercovered_data], \
            lcd[kn.pertinent_undercovered_list_col]
        assert lcd[kn.additional_undercovered_list_col] == [], lcd[kn.additional_undercovered_list_col]

        # NPLC
        lcd = self.v.determine_low_coverage_type(data=additional_undercovered_data, low_coverage_dict=lcd)
        assert lcd[kn.pertinent_negatives_list_col] == [pertinent_negative_data], lcd[kn.pertinent_negatives_list_col]
        assert lcd[kn.pertinent_undercovered_list_col] == [pertinent_undercovered_data],\
            lcd[kn.pertinent_undercovered_list_col]
        assert lcd[kn.additional_undercovered_list_col] == [additional_undercovered_data], \
            lcd[kn.additional_undercovered_list_col]

        # PN again
        lcd = self.v.determine_low_coverage_type(data=pertinent_negative_v2_data, low_coverage_dict=lcd)
        assert sorted(lcd[kn.pertinent_negatives_list_col]) == sorted([pertinent_negative_data,
                                                                       pertinent_negative_v2_data]), \
            sorted(lcd[kn.pertinent_negatives_list_col])
        assert lcd[kn.pertinent_undercovered_list_col] == [pertinent_undercovered_data], \
            lcd[kn.pertinent_undercovered_list_col]
        assert lcd[kn.additional_undercovered_list_col] == [additional_undercovered_data],\
            lcd[kn.additional_undercovered_list_col]
