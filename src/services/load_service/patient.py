import subprocess
import pandas as pd


class Patient:

    def __init__(self, db):

        self.db = db
        self.load_dict = {
            'csv': self.load_csv,
            'pkl': self.load_pkl,
            'bson': self.load_bson
        }
        self.clinical_df = None
        self.genomic_df = None

    def load_csv(self, clinical, genomic):
        """Load CSV file into a Pandas dataframe"""
        self.clinical_df = pd.read_csv(clinical)
        self.genomic_df = pd.read_csv(genomic, low_memory=False)

    def load_pkl(self, clinical, genomic):
        """Load PKL file into a Pandas dataframe"""
        self.clinical_df = pd.read_pickle(clinical)
        self.genomic_df = pd.read_pickle(genomic)

    @staticmethod
    def load_bson(clinical, genomic):
        """Load bson file into MongoDB"""
        cmd1 = "mongorestore --host localhost:27017 --db matchminer %s" % clinical
        cmd2 = "mongorestore --host localhost:27017 --db matchminer %s" % genomic
        subprocess.call(cmd1.split(' '))
        subprocess.call(cmd2.split(' '))
        return True
