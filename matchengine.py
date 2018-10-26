"""Copyright 2016 Dana-Farber Cancer Institute"""

import time
import argparse
import subprocess

# from matchengine.engine import MatchEngine
from src.utilities.utilities import get_db
from src.services.load_service.load_main import load_service

MONGO_URI = ""
MONGO_DBNAME = "matchminer"
MATCH_FIELDS = "mrn,sample_id,first_last,protocol_no,nct_id,genomic_alteration,tier,match_type," \
               "trial_accrual_status,match_level,code,internal_id,ord_physician_name,ord_physician_email," \
               "vital_status,oncotree_primary_diagnosis_name,true_hugo_symbol,true_protein_change," \
               "true_variant_classification,variant_category,report_date,chromosome,position," \
               "true_cdna_change,reference_allele,true_transcript_exon,canonical_strand,allele_fraction," \
               "cnv_call,wildtype,_id"





# def export_results(file_format, outpath):
#     """Return csv file containing the match results to the current working directory"""
#     cmd = "mongoexport --host localhost:27017 --db matchminer -c trial_match --fields {0} " \
#           "--type {1} --out {2}.{1}".format(MATCH_FIELDS, file_format, outpath)
#     subprocess.call(cmd.split(' '))
#
#
# def match(args):
#     """
#     Matches all trials in database to patients
#
#     :param daemon: Boolean flag; when true, runs the matchengine once per 24 hours.
#     """
#
#     db = get_db(args.mongo_uri)
#
#     while True:
#         me = MatchEngine(db)
#         me.find_trial_matches()
#
#         # exit if it is not set to run as a nightly automated daemon, otherwise sleep for a day
#         if not args.daemon:
#
#             # choose output file format
#             if args.json_format:
#                 file_format = 'json'
#             elif args.outpath and len(args.outpath.split('.')) > 1:
#                 file_format = args.outpath.split('.')[-1]
#                 if file_format not in ['json', 'csv']:
#                     file_format = 'csv'
#             else:
#                 file_format = 'csv'
#
#             # choose output path
#             if args.outpath:
#                 outpath = args.outpath.split('.')[0]
#             else:
#                 outpath = './results'
#
#             # export results
#             export_results(file_format, outpath)
#
#             break
#         else:
#             time.sleep(86400)   # sleep for 24 hours


if __name__ == '__main__':

    param_trials_help = 'Path to your trial data file or a directory containing a file for each trial.' \
                        'Default expected format is YML.'
    param_mongo_uri_help = 'Your MongoDB URI. If you do not supply one it will default to whatever is set to ' \
                           '"MONGO_URI" in your secrets file. ' \
                           'See https://docs.mongodb.com/manual/reference/connection-string/ for more information.'
    param_daemon_help = 'Set to launch the matchengine as a nightly automated process'
    param_clinical_help = 'Path to your clinical file. Default expected format is CSV.'
    param_genomic_help = 'Path to your genomic file. Default expected format is CSV'
    param_json_help = 'Set this flag to export your results in a .json file.'
    param_csv_help = 'Set this flag to export your results in a .csv file. Default.'
    param_outpath_help = 'Destination and name of your results file.'
    param_trial_format_help = 'File format of input trial data. Default is YML.'
    param_patient_format_help = 'File format of input patient data (both clinical and genomic files). Default is CSV.'

    # mode parser.
    parser = argparse.ArgumentParser()
    subp = parser.add_subparsers(help='sub-command help')

    # load_service
    subp_p = subp.add_parser('load', help='Sets up your MongoDB for matching.')
    subp_p.add_argument('-t', dest='trials', help=param_trials_help)
    subp_p.add_argument('-c', dest='clinical', help=param_clinical_help)
    subp_p.add_argument('-g', dest='genomic', help=param_genomic_help)
    subp_p.add_argument('--mongo-uri', dest='mongo_uri', required=False, default=None, help=param_mongo_uri_help)
    subp_p.add_argument('--trial-format',
                        dest='trial_format',
                        default='yml',
                        action='store',
                        choices=['yml', 'json', 'bson'],
                        help=param_trial_format_help)
    subp_p.add_argument('--patient-format',
                        dest='patient_format',
                        default='csv',
                        action='store',
                        choices=['csv', 'pkl', 'bson'],
                        help=param_patient_format_help)
    subp_p.set_defaults(func=load_service)
    #
    # # match
    # subp_p = subp.add_parser('match', help='Matches all trials in database to patients')
    # subp_p.add_argument('--mongo-uri', dest='mongo_uri', required=False, default=None, help=param_mongo_uri_help)
    # subp_p.add_argument('--daemon', dest="daemon", required=False, action="store_true", help=param_daemon_help)
    # subp_p.add_argument('--json', dest="json_format", required=False, action="store_true", help=param_json_help)
    # subp_p.add_argument('--csv', dest="csv_format", required=False, action="store_true", help=param_csv_help)
    # subp_p.add_argument('-o', dest="outpath", required=False, help=param_outpath_help)
    # subp_p.set_defaults(func=match)

    # parse args.
    args = parser.parse_args()
    args.func(args)
