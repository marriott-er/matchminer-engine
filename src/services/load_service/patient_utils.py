import logging
import subprocess
import pandas as pd

from src.utilities import settings as s
from src.data_store import key_names as kn

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s', )


class PatientUtils:

    def __init__(self, db):

        self.load_dict = {
            'csv': self.load_csv,
            'pkl': self.load_pkl,
            'bson': self.load_bson
        }
        self.clinical_df = None
        self.genomic_df = None
        self.cdtypes = {kn.mrn_col: str, kn.alt_mrn_col: str}
        self.gdtypes = {kn.coverage_col: float, kn.chromosome_col: str}
        self.true_values = ['TRUE', 'True', 'true']
        self.false_values = ['FALSE', 'False', 'false']
        self.db = db

    def load_csv(self, clinical, genomic, **kwargs):
        """
        Load CSV file into a Pandas dataframe

        :param clinical: {str} Path to clinical CSV
        :param genomic: {str} Path to genomic CSV
        :return: {null}
        """

        self.clinical_df = pd.read_csv(clinical).astype(self.cdtypes)
        self.genomic_df = pd.read_csv(genomic,
                                      low_memory=False,
                                      true_values=self.true_values,
                                      false_values=self.false_values).astype(self.gdtypes)

    def load_pkl(self, clinical, genomic, **kwargs):
        """
        Load PKL file into a Pandas dataframe

        :param clinical: {str} Path to clinical PKL
        :param genomic: {str} Path to genomic PKL
        :return: {null}
        """
        self.clinical_df = pd.read_pickle(clinical).astype(self.cdtypes)
        self.genomic_df = pd.read_pickle(genomic).astype(self.gdtypes)

    def load_bson(self, clinical, genomic, lc=None):
        """
        Load BSON file into a Pandas dataframe

        :param clinical: {str} Path to clinical BSON
        :param genomic: {str} Path to genomic BSON

        :return: {null}
        """

        # load BSON into Pandas DF
        cmd = 'mongorestore --uri %s --db %s {0}' % (s.MONGO_URI, s.MONGO_DBNAME)

        if clinical is not None:
            subprocess.call(cmd.format(clinical).split())
            self.clinical_df = pd.DataFrame.from_records(self.db.clinical.find())

        if genomic is not None:
            subprocess.call(cmd.format(genomic).split())
            self.genomic_df = pd.DataFrame.from_records(self.db.genomic.find())

        if lc is not None:
            subprocess.call(cmd.format(lc).split())
            self.genomic_df = self.genomic_df.append(pd.DataFrame.from_records(self.db.negative_genomic.find()))

        # rename columns
        self.clinical_df.rename(index=str, columns=s.rename_clinical, inplace=True)
        self.genomic_df.rename(index=str, columns=s.rename_genomic, inplace=True)


    @staticmethod
    def load_samples_bson(samples_bson):
        """
        Load bson file into MongoDB

        :param samples_bson: {str} Path to samples BSON
        :return: {null}
        """
        logging.info('Restoring samples data from %s' % samples_bson)
        cmd = "mongorestore --uri %s --db %s %s" % (s.MONGO_URI, s.MONGO_DBNAME, samples_bson)
        subprocess.call(cmd.split())
        return True
