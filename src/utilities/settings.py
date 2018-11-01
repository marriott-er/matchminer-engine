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

# clinical fields
sample_id_col = 'sampleId'
birth_date_col = 'birthDate'
report_date_col = 'reportDate'
diagnosis_col = 'oncotreePrimaryDiagnosisName'

# mutation fields
variant_category_col = 'variantCategory'
gene_col = 'trueHugoSymbol'
chromosome_col = 'chromosome'
position_col = 'position'
strand_col = 'trueStrand'
exon_col = 'trueTranscriptExon'
variant_class_col = 'trueVariantClassification'
protein_change_col = 'trueProteinChange'
cdna_change_col = 'trueCDNAChange'
transcript_col = 'treuCDNATranscriptId'
alt_allele_col = 'alternateAllele'
ref_allele_col = 'referenceAllele'
ref_residue_col = 'referenceResidue'
allele_fraction_col = 'alleleFraction'
transcript_src_col = 'transcriptSource'
coverage_col = 'coverage'
somatic_status_col = 'somaticStatus'
tier_col = 'tier'
mutation_cols = [variant_category_col, gene_col, chromosome_col, position_col, strand_col, exon_col, variant_class_col,
                 protein_change_col, cdna_change_col, transcript_col, alt_allele_col, ref_allele_col, ref_residue_col,
                 allele_fraction_col, transcript_src_col, coverage_col, somatic_status_col, tier_col]

# cnv fields
cytoband_col = 'cytoband'
cnv_call_col = 'cnvCall'
cnv_band_col = 'cnvBand'
copy_count_col = 'copyCount'
cnv_row_id_col = 'cnvRowId'
actionability_col = 'actionability'
cnv_cols = [variant_category_col, gene_col, cytoband_col, cnv_call_col, cnv_band_col,
            copy_count_col, cnv_row_id_col, actionability_col]

# sv fields
sv_comment_col = 'structuralVariantComment'
sv_cols = [variant_category_col, sv_comment_col]

# genomic values
variant_category_mutation_val = 'MUTATION'
variant_category_cnv_val = 'CNV'
variant_category_sv_val = 'SV'
variant_class_missense_mutation_val = 'Missense_Mutation'
