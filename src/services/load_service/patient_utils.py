import logging
import subprocess
import pandas as pd

from src.utilities import settings as s
from src.data_store import key_names as kn
from src.utilities.utilities import set_dtypes
from src.utilities.utilities import load_table_in_chunks

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s', )


class PatientUtils:

    def __init__(self, db, mongo_uri, mongo_dbname):

        self.load_dict = {
            'csv': self.load_csv,
            'pkl': self.load_pkl,
            'bson': self.load_bson
        }
        self.clinical_df = None
        self.genomic_df = None
        self.cdtypes = {
            kn.mrn_col: str,
            kn.alt_mrn_col: str,
            kn.pdf_layout_version_col: int
        }
        self.gdtypes = {
            kn.coverage_col: int,
            kn.chromosome_col: str,
        }
        self.true_values = ['TRUE', 'True', 'true']
        self.false_values = ['FALSE', 'False', 'false']
        self.db = db
        self.mongo_uri = mongo_uri
        self.mongo_dbname = mongo_dbname

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
        cmd = 'mongorestore --uri %s --db %s {0}' % (self.mongo_uri, self.mongo_dbname)

        if clinical is not None:
            subprocess.call(cmd.format(clinical).split())
            self.clinical_df = pd.DataFrame.from_records(self.db.clinical.find())
            self.clinical_df.rename(index=str, columns=s.rename_clinical, inplace=True)
            self.clinical_df = set_dtypes(df=self.clinical_df, dtype_dict=self.cdtypes)

        if genomic is not None:
            subprocess.call(cmd.format(genomic).split())
            self.genomic_df = load_table_in_chunks(db=self.db, table_name='genomic')
            self.genomic_df.rename(index=str, columns=s.rename_genomic, inplace=True)
            self.genomic_df = set_dtypes(df=self.genomic_df, dtype_dict=self.gdtypes)

            print '---debug---'
            print self.genomic_df.head(1).T
            print self.genomic_df.dtypes
            assert False
            # todo here

        if lc is not None:
            subprocess.call(cmd.format(lc).split())
            lc_df = pd.DataFrame.from_records(self.db.negative_genomic.find())
            lc_df.rename(index=str, columns=s.rename_lc, inplace=True)
            lc_df[kn.variant_category_col] = s.variant_category_lc_val
            self.genomic_df = self.genomic_df.append(lc_df)

    def load_samples_bson(self, samples_bson):
        """
        Load bson file into MongoDB

        :param samples_bson: {str} Path to samples BSON
        :return: {null}
        """
        logging.info('Restoring samples data from %s' % samples_bson)
        cmd = "mongorestore --uri %s --db %s %s" % (self.mongo_uri, self.mongo_dbname, samples_bson)
        subprocess.call(cmd.split())
        return True
