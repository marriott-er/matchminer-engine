import subprocess
import pandas as pd

from src.utilities import settings as s
from src.data_store import key_names as kn


class PatientUtilities:

    def __init__(self):

        self.load_dict = {
            'csv': self.load_csv,
            'pkl': self.load_pkl,
            'bson': self.load_bson
        }
        self.clinical_df = None
        self.genomic_df = None

    def load_csv(self, clinical, genomic):
        """
        Load CSV file into a Pandas dataframe

        :param clinical: {str} Path to clinical CSV
        :param genomic: {str} Path to genomic CSV
        :return: {null}
        """
        cdtypes = {kn.mrn_col: str, kn.alt_mrn_col: str}
        self.clinical_df = pd.read_csv(clinical).astype(cdtypes)

        gdtypes = {kn.coverage_col: float, kn.chromosome_col: str}
        self.genomic_df = pd.read_csv(genomic,
                                      low_memory=False,
                                      true_values=['TRUE', 'True', 'true'],
                                      false_values=['FALSE', 'False', 'false']).astype(gdtypes)

    def load_pkl(self, clinical, genomic):
        """
        Load PKL file into a Pandas dataframe

        :param clinical: {str} Path to clinical PKL
        :param genomic: {str} Path to genomic PKL
        :return: {null}
        """
        self.clinical_df = pd.read_pickle(clinical)
        self.genomic_df = pd.read_pickle(genomic)

    @staticmethod
    def load_bson(samples_bson):
        """
        Load bson file into MongoDB

        :param samples_bson: {str} Path to samples BSON
        :return: {null}
        """
        cmd = "mongorestore --uri %s --db %s %s" % (s.MONGO_URI, s.MONGO_DBNAME, samples_bson)
        subprocess.call(cmd.split(' '))
        return True