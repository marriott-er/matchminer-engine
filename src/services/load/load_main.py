import logging
import pandas as pd
import datetime as dt
from pymongo import ASCENDING, DESCENDING

from src.utilities import settings as s
from src.utilities.utilities import get_db, dataframe_to_json
from src.services.load.patient import Patient
from src.services.load.trial import Trial

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s', )


def load_main(args):
    """
    Sets up MongoDB for matching

    :param args: clinical: Path to csv file containing clinical data. Required fields are:
        - MRN                           {str} (Unique patient identifier)
        - sampleId                      {str} (Unique sample identifier)
        - oncotreePrimaryDiagnosisName  {str} (Disease diagnosis)
        - birthDate                     {str -> datetime object} (Date of birth in format 'YYYY-MM-DD 00:00:00')

        Suggested additional fields:
        - ordPhysicianName              {str}
        - ordPhysicianEmail             {str}
        - reportDate                    {str -> datetime object} (format 'YYYY-MM-DD 00:00:00')
        - vitalStatus                   {str} (alive or deceased)
        - firstLast                     {str} (Patient's first and last name)
        - gender                        {str} (Male or Female)

    :param args: genomic: Path to csv file containing genomic data. The following fields are used in matching:
        - sample_id                     {str} (Unique sample identifier)
        - trueHugoSymbol                {str} (Gene name)
        - trueProteinChange             {str} (Specific variant)
        - trueVariantClassification     {str} (Variant type)
        - variantCategory               {str} (CNV, MUTATION, or SV)
        - trueTranscriptExon            {int} (Exon number)
        - cnvCall                       {str} (Heterozygous deletion, Homozygous deletion,
                                               Gain, High Level amplification, or null)
        - wildtype                      {bool}

        Suggested additional fields:
        - chromosome                    {str}
        - position                      {int}
        - trueCDNAChange                {str}
        - referenceAllele               {str}
        - trueStrand                    {str} (- or +)
        - alleleFraction                {float}
        - {tier}                        {int}

    :param args: trials: Path to bson trial file.
    """
    exe = Load(args)

    # insert trial data
    if args.trials:
        exe.add_trial_data_to_mongo()

    # load patient data
    if args.clinical:
        exe.load_patient_data()

        if not exe.clinical_is_bson:
            exe.reformat_clinical_dates()

        # add to mongo
        exe.add_clinical_data_to_mongo()
        # exe.create_clinical_index()  # todo enable this


class Load:

    def __init__(self, args):
        self._args = args
        self.db = get_db(self._args.mongo_uri)
        self.t = Trial(self.db)
        self.p = Patient(self.db)
        self.clinical_is_bson = False
        self.date_cols = [s.birth_date_col, s.report_date_col]
        self.date_format = '%Y-%m-%d %X'

    def add_trial_data_to_mongo(self):
        """
        Insert trial documents to MongoDB

        :return: {null}
        """
        logging.info('Adding trials to mongo...')
        self.t.load_dict[self._args.trial_format](self._args.trials)

    def load_patient_data(self):
        """
        Insert sample documents into MongoDB

        :return: {null}
        """

        # both clinical and genomic files must be supplied
        if not self._args.genomic:
            raise ValueError('Genomic file must be supplied along with clinical file.')

        logging.info('Reading data into pandas...')
        self.clinical_is_bson = self.p.load_dict[self._args.patient_format](self._args.clinical, self._args.genomic)

    def reformat_clinical_dates(self):
        """
        Reformat data values to the appropriate types

        :return: {null}
        """

        # change date column values from strings to datetime objects
        for col in self.date_cols:
            try:
                self.p.clinical_df[col] = self.p.clinical_df[col].apply(
                    lambda x: str(dt.datetime.strptime(x, self.date_format)))
            except ValueError as exc:
                if col == s.birth_date_col:
                    logging.warning('Birth dates should be formatted %Y-%m-%d to be properly stored in MongoDB.')
                    logging.warning('Birth dates may be malformed in the database and will therefore not match'
                                    'trial age restrictions properly.')
                    logging.warning('Caught system error: %s' % exc)

        # change exon to type integer
        self.p.genomic_df[s.true_transcript_exon_col] = self.p.genomic_df[s.true_transcript_exon_col].apply(
            lambda x: int(x) if x != '' and pd.notnull(x) else x)

    def add_clinical_data_to_mongo(self):
        """
        Insert the clinical dataframe to MongoDB

        :return: {null}
        """
        logging.info('Adding clinical data to mongo...')
        clinical_json = dataframe_to_json(df=self.p.clinical_df)
        for item in clinical_json:
            item[s.variants_col] = self._add_genomic_data_to_clinical_dataframe(clinical_json=item)
            for col in self.date_cols:
                if col in item:
                    item[col] = dt.datetime.strptime(str(item[col]), self.date_format)

        self.db.clinical.insert(clinical_json)

    def _add_genomic_data_to_clinical_dataframe(self, clinical_json):
        """
        Add the genomic data to the "variants" column of the clinical documents

        :param clinical_json: {single JSON object}
        :return: {list of JSON objects}
        """
        f1 = (self.p.genomic_df[s.sample_id_col] == clinical_json[s.sample_id_col])
        gdf = self.p.genomic_df[f1]
        genomic_json = dataframe_to_json(df=gdf)
        return genomic_json

    def create_clinical_index(self):
        """
        Insert a clinical MongoDB index

        :return: {null}
        """
        raise NotImplementedError
        # logging.info('Creating index...')
        # self.db.genomic.create_index([("TRUE_HUGO_SYMBOL", ASCENDING), ("WILDTYPE", ASCENDING)])
