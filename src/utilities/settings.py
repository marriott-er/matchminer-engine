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


# clinical columns
sample_id_col = 'sampleId'
birth_date_col = 'birthDate'
report_date_col = 'reportDate'

# genomic columns
variants_col = 'variants'
true_transcript_exon_col = 'trueTranscriptExon'
