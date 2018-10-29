import os
import sys
import json
import logging

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


sample_collection_name = 'samples'
variants_key = 'variants'
snv_key = 'snvs'
cnv_key = 'cnvs'
sv_key = 'svs'
signature_key = 'signatures'
genomic_variants_subheader_keys = [snv_key, cnv_key, sv_key, signature_key]

# clinical fields
sample_id_col = 'sampleId'
birth_date_col = 'birthDate'
report_date_col = 'reportDate'
diagnosis_col = 'oncotreePrimaryDiagnosisName'

# genomic fields
gene_name_col = 'trueHugoSymbol'
ref_residue_col = 'referenceResidue'
variant_category_col = 'variantCategory'
protein_change_col = 'trueProteinChange'
cnv_call_col = 'cnvCall'
sv_comment_col = 'structuralVariantComment'
mmr_col = 'mmrStatus'
true_transcript_exon_col = 'trueTranscriptExon'
variant_class_col = 'trueVariantClassification'

# genomic values
mutation_val = 'MUTATION'
cnv_val = 'CNV'
missense_mutation_val = 'Missense_Mutation'
