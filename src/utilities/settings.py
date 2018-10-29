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


# clinical settings
sample_collection_name = 'samples'
sample_id_col = 'sampleId'
birth_date_col = 'birthDate'
report_date_col = 'reportDate'

# genomic settings
variants_col = 'variants'
variant_class_col = 'trueVariantClassification'
true_transcript_exon_col = 'trueTranscriptExon'
gene_name_col = 'trueHugoSymbol'
variant_category_col = 'variantCategory'
ref_residue_col = 'referenceResidue'
protein_change_col = 'trueProteinChange'
genomic_variants_subheader_keys = ['snvs', 'cnvs', 'svs', 'signatures']

mutation_val = 'MUTATION'
cnv_val = 'CNV'
missense_mutation_val = 'Missense_Mutation'
