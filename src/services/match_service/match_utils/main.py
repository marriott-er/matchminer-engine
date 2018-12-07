import logging
import subprocess
from apscheduler.schedulers.blocking import BlockingScheduler

from src.utilities import settings as s
from src.data_store.trial_matches_data_model import trial_matches_schema
from src.services.match_service.match_utils.shared_utils import SharedUtils
from src.services.match_service.match_utils.trial_utils import TrialUtils

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s', )


def export_results(args, file_format, outpath):
    """
    Create file containing the match results

    :param args: {argparse command-line arguments}
    :param file_format: {str}
    :param outpath: {str}
    """
    cmd = 'mongoexport ' \
          '--uri {mongo_uri} ' \
          '--db {mongo_dbname} ' \
          '--collection {trial_match_collection} ' \
          '--fields {trial_match_fields} ' \
          '--type {file_format} ' \
          '--out {outpath}'.format(mongo_uri=args.mongo_uri if args.mongo_uri is not None else s.MONGO_URI,
                                   mongo_dbname=args.mongo_dbname if args.mongo_dbname is not None else s.MONGO_DBNAME,
                                   trial_match_collection=s.trial_match_collection_name,
                                   trial_match_fields=trial_matches_schema.keys(),
                                   file_format=file_format,
                                   outpath='%s.%s' % (outpath, file_format))
    subprocess.call(cmd.split(' '))


def match_service_scheduler(args):
    """Schedule Matchengine run execution"""

    main(args)
    if not args.now:
        scheduler = BlockingScheduler()
        scheduler.add_job(main, trigger='cron', hour='4', args=[args])
        scheduler.print_jobs()
        scheduler.start()
    else:
        # choose output file format
        if args.json_format:
            file_format = 'json'
        elif args.outpath and len(args.outpath.split('.')) > 1:
            file_format = args.outpath.split('.')[-1]
            if file_format not in ['json', 'csv']:
                file_format = 'csv'
        else:
            file_format = 'csv'

        # choose output path
        if args.outpath:
            outpath = args.outpath.split('.')[0]
        else:
            outpath = './results'

        # export results
        export_results(args, file_format, outpath)


def main(args):
    """Execute Matchengine"""

    utils = SharedUtils(args.mongo_uri, args.mongo_dbname)

    # parse input arguments
    trials = utils.find_trials()
    print '---debug---'
    for trial in trials:

        # parse trial document for all match trees
        trial_utils = TrialUtils(trial=trial)
        matchengines = trial_utils.parse_match_trees_from_trial()
        for matchengine in matchengines:

            # create match tree
            matchengine.convert_match_tree_to_digraph()

            # crate mongo query from match tree and find matching records
            matchengine.traverse_match_tree()

            # create trial matches records
            matchengine.create_trial_match_records()
            trial_matches_df = matchengine.sort_trial_matches()

            # save results
            utils.add_trial_matches(trial_matches_df=trial_matches_df)

    logging.info('DONE')
