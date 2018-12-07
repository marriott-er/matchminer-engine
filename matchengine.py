"""Copyright 2016 Dana-Farber Cancer Institute"""

import argparse

from src.services.load_service.load_main import load_service
from src.services.match_service.match_utils.main import match_service_scheduler

if __name__ == '__main__':

    param_trials_help = 'Path to your trial old_data file or a directory containing a file for each trial.' \
                        'Default expected format is YML.'
    param_mongo_uri_help = 'Your MongoDB URI. If you do not supply one it will default to whatever is set to ' \
                           '"MONGO_URI" in your secrets file. ' \
                           'See https://docs.mongodb.com/manual/reference/connection-string/ for more information.'
    param_daemon_help = 'Set to launch the old_matchengine as a nightly automated process'
    param_clinical_help = 'Path to your clinical file. Default expected format is CSV.'
    param_genomic_help = 'Path to your genomic file. Default expected format is CSV.'
    param_samples_help = 'Path to your samples BSON file.'
    param_lc_help = 'Path to your low coverage BSON file.'
    param_json_help = 'Set this flag to export your results in a .json file.'
    param_csv_help = 'Set this flag to export your results in a .csv file. Default.'
    param_outpath_help = 'Destination and name of your results file.'
    param_trial_format_help = 'File format of input trial old_data. Default is YML.'
    param_sample_format_help = 'File format of input patient old_data (both clinical and genomic files). ' \
                               'Default is CSV.'

    # mode parser.
    parser = argparse.ArgumentParser()
    subp = parser.add_subparsers(help='sub-command help')

    # load_service
    subp_p = subp.add_parser('load', help='Sets up your MongoDB for matching.')
    subp_p.add_argument('-t', dest='trials', help=param_trials_help)
    subp_p.add_argument('-c', dest='clinical', help=param_clinical_help)
    subp_p.add_argument('-g', dest='genomic', help=param_genomic_help)
    subp_p.add_argument('-s', dest='samples', help=param_samples_help)
    subp_p.add_argument('-lc', dest='low_coverage', help=param_lc_help)
    subp_p.add_argument('--mongo-uri', dest='mongo_uri', required=False, default=None, help=param_mongo_uri_help)
    subp_p.add_argument('--mongo-dbname', dest='mongo_dbname', required=False, default=None, help=param_mongo_uri_help)
    subp_p.add_argument('--trial-format',
                        dest='trial_format',
                        default='yml',
                        action='store',
                        choices=['yml', 'json', 'bson'],
                        help=param_trial_format_help)
    subp_p.add_argument('--sample-format',
                        dest='sample_format',
                        default='csv',
                        action='store',
                        choices=['csv', 'pkl', 'bson'],
                        help=param_sample_format_help)
    subp_p.set_defaults(func=load_service)

    # match
    subp_p = subp.add_parser('match', help='Matches all trials in database to patients')
    subp_p.add_argument('--mongo-uri', dest='mongo_uri', required=False, default=None, help=param_mongo_uri_help)
    subp_p.add_argument('--mongo-dbname', dest='mongo_dbname', required=False, default=None, help=param_mongo_uri_help)
    subp_p.add_argument('--now', dest="now", required=False, action="store_true", help=param_daemon_help)
    subp_p.add_argument('--json', dest="json_format", required=False, action="store_true", help=param_json_help)
    subp_p.add_argument('--csv', dest="csv_format", required=False, action="store_true", help=param_csv_help)
    subp_p.add_argument('-o', dest="outpath", required=False, help=param_outpath_help)
    subp_p.set_defaults(func=match_service_scheduler)

    # parse args.
    args = parser.parse_args()
    args.func(args)
