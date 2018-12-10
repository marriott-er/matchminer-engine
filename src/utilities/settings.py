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
date_cols = [kn.birth_date_col, kn.report_date_col, kn.date_received_at_seq_center_col]

# sample table settings
sample_collection_name = 'samples'
trial_match_collection_name = 'trialmatches'
variant_category_mutation_val = 'MUTATION'
variant_category_wildcard_mutation_val = 'WILDCARD_MUTATION'
variant_category_variant_class_val = 'VARIANT_CLASS_MUTATION'
variant_category_exon_val = 'EXON'
variant_category_cnv_val = 'CNV'
variant_category_sv_val = 'SV'
variant_category_signature_val = 'SIGNATURE'
variant_category_wt_val = 'WILDTYPE'
variant_category_lc_val = 'LOW_COVERAGE'
variant_category_any_val = 'ANY'
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
trial_coordinating_center_col = 'coordinating_center'
coordinating_center_dfci_val = 'Dana-Farber Cancer Institute'

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
mt_any_vc_val = 'Any Variation'
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

# rename old column names to new column names
rename_clinical = {
    'MRN': kn.mrn_col,
    'SAMPLE_ID': kn.sample_id_col,
    'BLOCK_NUMBER': kn.block_no_col,
    'data_push_id': kn.data_push_id_col,
    'ALT_MRN': kn.alt_mrn_col,
    'PATIENT_ID': kn.patient_id_col,
    'POWERPATH_PATIENT_ID': kn.powerpath_patient_id_col,
    'GENDER': kn.gender_col,
    'FIRST_NAME': kn.first_name_col,
    'LAST_NAME': kn.last_name_col,
    'BIRTH_DATE': kn.birth_date_col,
    'VITAL_STATUS': kn.vital_status_col,
    'DISEASE_CENTER_DESCR': kn.disease_center_descr_col,
    'ORD_PHYSICIAN_NAME': kn.ord_physician_name_col,
    'ORD_PHYSICIAN_NPI': kn.ord_physician_npi_col,
    'ORD_PHYSICIAN_EMAIL': kn.ord_physicians_email_col,
    'PATHOLOGIST_NAME': kn.pathologist_name_col,
    'LAST_VISIT_DATE': kn.last_visit_date_col,
    'PANEL_VERSION': kn.panel_version_col,
    'REPORT_COMMENT': kn.report_comment_col,
    'DATE_RECEIVED_AT_SEQ_CENTER': kn.date_received_at_seq_center_col,
    'REPORT_DATE': kn.report_date_col,
    'REPORT_VERSION': kn.report_version_col,
    'TEST_TYPE': kn.test_type_col,
    'QC_RESULT': kn.qc_result_col,
    'CNV_RESULTS': kn.cnv_results_col,
    'SNV_RESULTS': kn.snv_results_col,
    'CANCER_TYPE_PERCENTILE': kn.cancer_type_percentile_col,
    'ALL_PROFILE_PERCENTILE': kn.all_profile_percentile_col,
    'METAMAIN_COUNT': kn.metamain_count_col,
    'CASE_COUNT': kn.case_count_col,
    'PDF_LAYOUT_VERSION': kn.pdf_layout_version_col,
    'TOTAL_READS': kn.total_reads_col,
    'TOTAL_ALIGNED_READS': kn.total_aligned_reads_col,
    'PCT_TARGET_BASE': kn.pct_target_base_col,
    'MEAN_SAMPLE_COVERAGE': kn.mean_sample_coverage_col,
    'TUMOR_MUTATIONAL_BURDEN_PER_MEGABASE': kn.tmb_col,
    'ONCOTREE_PRIMARY_DIAGNOSIS': kn.oncotree_primary_diagnosis_col,
    'ONCOTREE_PRIMARY_DIAGNOSIS_NAME': kn.oncotree_primary_diagnosis_name_col,
    'ONCOTREE_BIOPSY_SITE': kn.oncotree_biopsy_site_col,
    'ONCOTREE_BIOPSY_SITE_TYPE': kn.oncotree_biopsy_site_type_col,
    'ONCOTREE_BIOPSY_SITE_NAME': kn.oncotree_biopsy_site_name_col,
    'ONCOTREE_BIOPSY_SITE_META': kn.oncotree_biopsy_site_meta_col,
    'ONCOTREE_BIOPSY_SITE_COLOR': kn.oncotree_biopsy_site_color_col,
    'TUMOR_PURITY_PERCENT': kn.tumor_purity_percent_col,
    'QUESTION1_YN': kn.q1_consent_col,
    'QUESTION2_YN': kn.q2_consent_col,
    'QUESTION3_YN': kn.q3_consent_col,
    'QUESTION4_YN': kn.q4_consent_col,
    'CRIS_YN': kn.cris_consent_col,
    'CONSENT_17000': kn.consent_17000_col
}
rename_genomic = {
    'SAMPLE_ID': kn.sample_id_col,
    'VARIANT_CATEGORY': kn.variant_category_col,
    'TRUE_HUGO_SYMBOL': kn.hugo_symbol_col,
    'CHROMSOME': kn.chromosome_col,
    'POSTION': kn.position_col,
    'TRUE_STRAND': kn.strand_col,
    'TRUE_TRANSCRIPT_EXON': kn.transcript_exon_col,
    'TRUE_VARIANT_CLASSIFICATION': kn.variant_class_col,
    'TRUE_PROTEIN_CHANGE': kn.protein_change_col,
    'TRUE_CDNA_CHANGE': kn.cdna_change_col,
    'TRUE_CDNA_TRANSCRIPT_ID': kn.cdna_transcript_id_col,
    'REFERENCE_GENOME': kn.ref_genomic_col,
    'ALTERNATE_ALLELE': kn.alt_allele_col,
    'REFERENCE_ALLELE': kn.ref_allele_col,
    'ALLELE_FRACTION': kn.allele_fraction_col,
    'TRANSCRIPT_SOURCE': kn.transcript_src_col,
    'COVERAGE': kn.coverage_col,
    'SOMATIC_STATUS': kn.somatic_status_col,
    'TIER': kn.tier_col,
    'TRUE_ENTREZ_ID': kn.entrez_id_col,
    'BEST': kn.is_best_effect_col,
    'CYTOBAND': kn.cytoband_col,
    'CNV_BAND': kn.cnv_band_col,
    'CNV_CALL': kn.cnv_call_col,
    'COPY_COUNT': kn.copy_count_col,
    'CNV_ROW_ID': kn.cnv_row_id_col,
    'ACTIONABILITY': kn.actionability_col,
    'STRUCTURAL_VARIANT_COMMENT': kn.sv_comment_col,
    'MMR_STATUS': kn.mmr_status_col,
    'TABACCO_STATUS': kn.tobacco_status_col,
    'TEMOZOLOMIDE_STATUS': kn.tmz_status_col,
    'POLE_STATUS': kn.pole_status_col,
    'APOBEC_STATUS': kn.apobec_status_col,
    'UVA_STATUS': kn.uva_status_col,
}
rename_lc = {
    'coverage_type': kn.coverage_type_col,
    'roi_type': kn.roi_type_col,
    'panel': kn.panel_col,
    'true_codon': kn.codon_col,
    'true_transcript_exon': kn.low_coverage_exon_col,
    'show_codon': kn.show_codon_col,
    'show_exon': kn.show_exon_col,
    kn.lc_coverage_col: kn.lc_coverage_col
}
