import os
import sys
import json
import logging

from src.data_store import key_names as kn

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s', )

MONGO_URI = ""
MONGO_DBNAME = ""

# pull secrets
file_path = os.getenv("SECRETS_JSON", None)

if file_path is None:
    logging.error("ENVAR SECRETS_JSON not set")

if file_path is not None:
    with open(file_path) as fin:
        vars = json.load(fin)
        for name, value in vars.iteritems():
            setattr(sys.modules[__name__], name, value)

# oncotree settings
TUMOR_TREE = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../', 'data/tumor_tree.txt'))
oncotree_all_solid_text = '_SOLID_'
oncotree_all_liquid_text = '_LIQUID_'

# sample table settings
sample_collection_name = 'samples'
variant_category_mutation_val = 'MUTATION'
variant_category_wildcard_mutation_val = 'WILDCARD_MUTATION'
variant_category_exon_val = 'EXON'
variant_category_cnv_val = 'CNV'
variant_category_sv_val = 'SV'
variant_category_signature_val = 'SIGNATURE'
variant_category_wt_val = 'WILDTYPE'
variant_category_lc_val = 'LOW_COVERAGE'
allowed_variants = [
    variant_category_mutation_val,
    variant_category_cnv_val,
    variant_category_sv_val,
    variant_category_signature_val,
    variant_category_wt_val,
    variant_category_lc_val
]

variant_class_missense_mutation_val = 'Missense_Mutation'
variant_class_nonsense_mutation_val = 'Nonsense_Mutation'
cnv_call_high_amp = 'High level amplification'
cnv_call_hetero_del = 'Heterozygous deletion'
cnv_call_homo_del = 'Homozygous deletion'
cnv_call_gain = 'Gain'
mmr_status_cannot_assess_val = 'Cannot assess'
mmr_status_indeterminate_val = 'Indeterminate (see note)'
mmr_status_proficient_val = 'Proficient'
mmr_status_deficient_val = 'Deficient'
ms_status_mss_val = 'MSS'
ms_status_msih_val = 'MSI-H'
pertinent_negative_val = 'PN'
pertinent_low_coverage_val = 'PLC'
additional_low_coverage_val = 'NPLC'
signature_cols = [
    kn.mmr_status_col,
    kn.ms_status_col,
    kn.tobacco_status_col,
    kn.tmz_status_col,
    kn.pole_status_col,
    kn.apobec_status_col,
    kn.uva_status_col
]
gcol_list = [
    kn.mutation_list_col,
    kn.cnv_list_col,
    kn.sv_list_col,
    kn.wt_genes_col,
    kn.pertinent_negatives_list_col,
    kn.pertinent_undercovered_list_col,
    kn.additional_undercovered_list_col
]

# trial table settings
trial_protocol_no_col = 'protocol_no'
trial_nct_id_col = 'nct_id'
trial_treatment_list_col = 'treatment_list'
trial_summary_col = '_summary'
trial_accrual_status_col = 'status'
trial_accrual_status_open_val = 'open to accrual'
trial_step_col = 'step'
trial_arm_col = 'arm'
trial_dose_col = 'dose_level'
trial_step_code_col = 'step_code'
trial_arm_code_col = 'arm_code'
trial_dose_code_col = 'level_code'
trial_match_tree_col = 'match'

# trial clinical criteria settings
mt_diagnosis = 'oncotree_primary_diagnosis'
mt_age = 'age_numerical'
mt_gender = 'gender'

# trial genomic criteria settings
mt_hugo_symbol = 'hugo_symbol'
mt_variant_category = 'variant_category'
mt_variant_class = 'variant_classification'
mt_protein_change = 'protein_change'
mt_wc_protein_change = 'wildcard_protein_change'
mt_exon = 'exon'
mt_cnv_call = 'cnv_call'
mt_wildtype = 'wildtype'
mt_mmr_status = 'mmr_status'
mt_ms_status = 'ms_status'
mt_tobacco_status = 'tobacco_status'
mt_tmz_status = 'tmz_status'
mt_pole_status = 'pole_status'
mt_apobec_status = 'apobec_status'
mt_uva_status = 'uva_status'
mt_signature_cols = [
    mt_mmr_status,
    mt_ms_status,
    mt_tobacco_status,
    mt_tmz_status,
    mt_pole_status,
    mt_apobec_status,
    mt_uva_status
]

mt_cnv_val = 'Copy Number Variation'
mt_mut_val = 'Mutation'
mt_sv_val = 'Structural Variation'
mt_high_amp_val = 'High Amplification'
mt_homo_del_val = 'Homozygous Deletion'
mt_hetero_del_val = 'Heterozygous Deletion'
mt_low_amp_val = 'Low Amplification'
mt_mmr_deficient_val = 'MMR-Deficient'
mt_mmr_proficient_val = 'MMR-Proficient'
mt_msi_high_val = 'MSI-H'
mt_mss_val = 'MSS'

# match table settings

match_accrual_status_open_val = 'open'
match_accrual_status_closed_val = 'closed'
