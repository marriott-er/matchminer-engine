from src.utilities import settings as s
from src.data_store import key_names as kn
from src.data_store import samples_data_model as sdm


def adjust_schema(schema):
    """
    Make certain fields that are required in the samples data model not required in the trial matches data model.

    :param schema: {dict}
    :return: {dict}
    """
    for field in schema:
        schema[field]['required'] = False

    return schema

accrual_status_allowed_vals = [s.match_accrual_status_open_val, s.match_accrual_status_closed_val]
trial_level_allowed_vals = ['step', 'arm', 'dose']

# Match reasons schemas
mutation_reasons_schema = adjust_schema(sdm.mutations_schema.copy())
mutation_reasons_schema[kn.mr_reason_level_col] = {'type': 'string', 'required': True,
                                                   'allowed': ['gene', 'exon', 'wildcard', 'variant']}
cnv_reasons_schema = adjust_schema(sdm.cnvs_schema.copy())
sv_reasons_schema = adjust_schema(sdm.svs_schema.copy())
wt_reasons_schema = adjust_schema(sdm.wts_schema.copy())
lc_reasons_schema = adjust_schema(sdm.low_coverage_schema.copy())

# Trial match schema
trial_matches_schema = {

    # basic information
    kn.sample_id_col: {'type': 'string', 'required': True},
    kn.tm_trial_protocol_no_col: {'type': 'string', 'required': True},
    kn.mrn_col: {'type': 'string', 'required': True},
    kn.vital_status_col: {'type': 'string', 'required': True, 'allowed': sdm.vital_status_allowed_vals},
    kn.tm_trial_accrual_status_col: {'type': 'string', 'required': True, 'allowed': accrual_status_allowed_vals},
    kn.tm_sort_order_col: {'type': 'integer', 'required': True},

    # trial reasons for matching
    kn.mr_trial_level_col: {'type': 'string', 'required': True, 'allowed': trial_level_allowed_vals},
    kn.mr_trial_step_code_col: {'type': 'string', 'required': True},
    kn.mr_trial_arm_code_col: {'type': 'string', 'nullable': True},
    kn.mr_trial_dose_code_col: {'type': 'string', 'nullable': True},
    kn.mr_coordinating_center_col: {'type': 'string', 'nullable': True},

    # genomic reasons for matching
    kn.mutation_list_col: {'type': 'list', 'schema': {'type': 'dict', 'schema': mutation_reasons_schema}},
    kn.cnv_list_col: {'type': 'list', 'schema': {'type': 'dict', 'schema': cnv_reasons_schema}},
    kn.sv_list_col: {'type': 'list', 'schema': {'type': 'dict', 'schema': sv_reasons_schema}},
    kn.wt_genes_col: {'type': 'list', 'schema': {'type': 'dict', 'schema': wt_reasons_schema}},
    kn.mr_low_coverage_list_col: {'type': 'list', 'schema': {'type': 'dict', 'schema': lc_reasons_schema}},

    # clinical reasons for matching
    kn.oncotree_primary_diagnosis_name_col: {'type': 'string', 'required': True},
    kn.mr_diagnosis_level_col: {'type': 'string', 'allowed': ['_solid_', '_liquid_', 'specific', None]},
    kn.birth_date_col: {'type': 'datetime', 'required': True},
    kn.gender_col: {'type': 'string', 'allowed': sdm.gender_allowed_vals},

    # mutational signature information
    kn.mmr_status_col: {
        'type': 'string',
        'allowed': [
            s.mmr_status_cannot_assess_val,
            s.mmr_status_indeterminate_val,
            s.mmr_status_proficient_val,
            s.mmr_status_deficient_val,
            None
        ],
        'nullable': True
    },
    kn.ms_status_col: {
        'type': 'string',
        'allowed': [
            s.mmr_status_cannot_assess_val,
            s.mmr_status_indeterminate_val,
            s.ms_status_mss_val,
            s.ms_status_msih_val,
            None
        ],
        'nullable': True
    },
    kn.tobacco_status_col: {'type': 'string', 'allowed': sdm.misc_signature_allowed_vals, 'nullable': True},
    kn.tmz_status_col: {'type': 'string', 'allowed': sdm.misc_signature_allowed_vals, 'nullable': True},
    kn.pole_status_col: {'type': 'string', 'allowed': sdm.misc_signature_allowed_vals, 'nullable': True},
    kn.apobec_status_col: {'type': 'string', 'allowed': sdm.misc_signature_allowed_vals, 'nullable': True},
    kn.uva_status_col: {'type': 'string', 'allowed': sdm.misc_signature_allowed_vals, 'nullable': True},

    # exclusion reasons for matching
    kn.genomic_exclusion_reasons_col: {'type': 'list', 'schema': {'type': 'dict', 'allow_unknown': True}},
    kn.clinical_exclusion_reasons_col: {'type': 'list', 'schema': {'type': 'dict', 'allow_unknown': True}}
}
