from src.utilities import settings as s
from src.data_store import key_names as kn
from src.data_store.samples_data_model import vital_status_allowed_vals, tier_allowed_vals, \
    actionability_allowed_vals, low_coverage_allowed_vals, gender_allowed_vals

accrual_status_allowed_vals = [s.match_accrual_status_open_val, s.match_accrual_status_closed_val]
trial_level_allowed_vals = ['step', 'arm', 'dose']

# Match reasons schemas
mutation_reasons_schema = {
    kn.mr_reason_level_col: {'type': 'string', 'required': True, 'allowed': ['gene', 'exon', 'wildcard', 'variant']},
    kn.mr_inclusion_criteria_col: {'type': 'boolean', 'required': True},
    kn.hugo_symbol_col: {'type': 'string', 'required': True},
    kn.transcript_exon_col: {'type': 'integer'},
    kn.variant_class_col: {'type': 'string'},
    kn.protein_change_col: {'type': 'string'},
    kn.ref_residue_col: {'type': 'string', 'nullable': True},
    kn.tier_col: {'type': 'integer', 'allowed': tier_allowed_vals, 'required': True}
}
cnv_reasons_schema = {
    kn.hugo_symbol_col: {'type': 'string', 'required': True},
    kn.cnv_call_col: {'type': 'string'},
    kn.actionability_col: {'type': 'string', 'required': True, 'nullable': True, 'allowed': actionability_allowed_vals}
}
sv_reasons_schema = {
    kn.sv_comment_col: {'type': 'string', 'required': True},
}
wt_reasons_schema = {
    kn.hugo_symbol_col: {'type': 'string', 'required': True}
}
lc_reasons_schema = {
    kn.hugo_symbol_col: {'type': 'string', 'required': True},
    kn.coverage_type_col: {'type': 'string', 'required': True, 'allowed': low_coverage_allowed_vals}
}

match_reasons_schema = {

    # trial reasons for matching
    kn.mr_trial_level_col: {'type': 'string', 'required': True, 'allowed': trial_level_allowed_vals},
    kn.mr_trial_step_code_col: {'type': 'string', 'required': True},
    kn.mr_trial_arm_code_col: {'type': 'string', 'nullable': True},
    kn.mr_trial_dose_code_col: {'type': 'string', 'nullable': True},

    # genomic reasons for matching
    kn.mr_mutation_list_col: {'type': 'list', 'schema': {'type': 'dict', 'schema': mutation_reasons_schema}},
    kn.mr_cnv_list_col: {'type': 'list', 'schema': {'type': 'dict', 'schema': cnv_reasons_schema}},
    kn.mr_sv_list_col: {'type': 'list', 'schema': {'type': 'dict', 'schema': sv_reasons_schema}},
    kn.mr_wildtype_list_col: {'type': 'list', 'schema': {'type': 'dict', 'schema': wt_reasons_schema}},
    kn.mr_low_coverage_list_col: {'type': 'list', 'schema': {'type': 'dict', 'schema': lc_reasons_schema}},

    # clinical reasons for matching
    kn.mr_diagnosis_col: {'type': 'string', 'required': True},
    kn.mr_age_col: {'type': 'string'},
    kn.mr_gender_col: {'type': 'string', 'allowed': gender_allowed_vals}
}

# Trial match schema
trial_matches_schema = {
    kn.tm_sample_id_col: {'type': 'string', 'required': True},
    kn.tm_trial_protocol_no_col: {'type': 'string', 'required': True},
    kn.tm_mrn_col: {'type': 'string', 'required': True},
    kn.tm_vital_status_col: {'type': 'string', 'required': True, 'allowed': vital_status_allowed_vals},
    kn.tm_trial_accrual_status_col: {'type': 'string', 'required': True, 'allowed': accrual_status_allowed_vals},
    kn.tm_sort_order_col: {'type': 'integer', 'required': True},
    kn.tm_match_reasons_col: {'type': 'list', 'schema': {'type': 'dict', 'schmea': match_reasons_schema}}
}