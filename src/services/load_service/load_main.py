import logging
import pandas as pd
import datetime as dt
from pandas.tslib import Timestamp
from pymongo import ASCENDING, DESCENDING

from src.utilities import settings as s
from src.utilities.utilities import handle_chromosome_column, handle_vc
from src.data_store import key_names as kn
from src.data_store.samples_data_model import samples_schema
from src.data_store.validator import SamplesValidator
from src.utilities.utilities import get_db, dataframe_to_json
from src.services.load_service.patient_utils import PatientUtils
from src.services.load_service.trial_utils import TrialUtils
from src.services.load_service.variants_utils import VariantsUtils

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s', )


def load_service(_args):
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
        - sampleId                      {str} (Unique sample identifier)
        - variantCategory               {str} (CNV, MUTATION, SV, SIGNATURE, WILDTYPE, LOW_COVERAGE) ** required
        - hugoSymbol                    {str} (Gene name)
        - proteinChange                 {str} (Specific variant)
        - variantClassification         {str} (Variant type)
        - transcriptExon                {int} (Exon number)
        - cnvCall                       {str} (Heterozygous deletion, Homozygous deletion,
                                               Gain, High Level amplification, or null)

        Suggested additional fields:
        - chromosome                    {str}
        - position                      {int}
        - cDNAChange                    {str}
        - referenceAllele               {str}
        - strand                        {str} (- or +)
        - alleleFraction                {float}
        - tier                          {int}

    :param args: trials: Path to bson trial file.
    """
    exe = LoadService(_args)

    # insert trial data
    if _args.trials:
        exe.add_trial_data_to_mongo()

    # load_service patient data
    if _args.clinical or _args.samples:
        exe.load_patient_data()

        if not exe.clinical_is_bson:
            exe.reformat_clinical_dates()

            # add to mongo
            exe.add_clinical_data_to_mongo()
            # exe.create_clinical_index()  # todo enable this


class LoadService:

    def __init__(self, args):
        self._args = args

        if self._args.mongo_uri is None:
            self._args.mongo_uri = s.MONGO_URI
        if self._args.mongo_dbname is None:
            self._args.mongo_dbname = s.MONGO_DBNAME

        self.db = get_db(mongo_uri=self._args.mongo_uri, mongo_dbname=self._args.mongo_dbname)
        self.t = TrialUtils(self.db, mongo_uri=self._args.mongo_uri, mongo_dbname=self._args.mongo_dbname)
        self.p = PatientUtils(self.db, mongo_uri=self._args.mongo_uri, mongo_dbname=self._args.mongo_dbname)
        self.validator = SamplesValidator(samples_schema)

        self.clinical_is_bson = False
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

        if self._args.samples:
            self.clinical_is_bson = self.p.load_samples_bson(samples_bson=self._args.samples)
            return

        # both clinical and genomic files must be supplied
        if self._args.clinical and not self._args.genomic:
            raise ValueError('Genomic file must be supplied along with clinical file.')

        logging.info('Reading data into pandas...')
        self.clinical_is_bson = self.p.load_dict[self._args.sample_format](self._args.clinical,
                                                                           self._args.genomic,
                                                                           self._args.low_coverage)

    def reformat_clinical_dates(self):
        """
        Reformat data values to the appropriate types

        :return: {null}
        """

        # change date column values from strings to datetime objects
        for col in s.date_cols:
            try:
                self.p.clinical_df[col] = self.p.clinical_df[col].apply(
                    lambda x: dt.datetime.strftime(x, self.date_format) if isinstance(x, Timestamp) else
                              str(dt.datetime.strptime(x, self.date_format)))
            except ValueError as exc:
                if col == kn.birth_date_col:
                    logging.warning('Birth dates should be formatted %Y-%m-%d to be properly stored in MongoDB.')
                    logging.warning('Birth dates may be malformed in the database and will therefore not match'
                                    'trial age restrictions properly.')
                    logging.warning('Caught system error: %s' % exc)

        # change exon to type integer
        self.p.genomic_df[kn.transcript_exon_col] = self.p.genomic_df[kn.transcript_exon_col].apply(
            lambda x: int(x) if x != '' and pd.notnull(x) else x)

    def add_clinical_data_to_mongo(self):
        """
        Insert the clinical dataframe to MongoDB

        :return: {null}
        """
        logging.info('Adding clinical data to mongo...')
        cols = [i for i in self.p.clinical_df.columns if i in s.rename_clinical.values()]
        clinical_json = dataframe_to_json(df=self.p.clinical_df[cols])
        for idx, sample_obj in enumerate(clinical_json):

            if idx % 1000 == 0:
                logging.info('Processed %d cases' % idx)

            # add genomic data
            sample_obj = self._add_genomic_data_to_clinical_dataframe(sample_obj=sample_obj)

            # convert date columns as datetime object
            for col in s.date_cols:
                if col in sample_obj:
                    sample_obj[col] = dt.datetime.strptime(str(sample_obj[col]), self.date_format)

            # convert integer columns to int
            for col in [k for k, v in self.p.cdtypes.iteritems() if v == int]:
                if col in sample_obj and sample_obj[col]:
                    sample_obj[col] = int(sample_obj[col])

            # Special type edge case for chromosome column
            for mutation in sample_obj[kn.mutation_list_col]:
                if kn.chromosome_col in mutation:
                    mutation[kn.chromosome_col] = handle_chromosome_column(mutation[kn.chromosome_col])

                # Integers are stored as floats in the dataframe because Pandas can't handle null values in a column
                # with an integer data type
                for col in [k for k, v in self.p.gdtypes.iteritems() if v == int]:
                    if col in mutation and pd.notnull(mutation[col]):
                        mutation[col] = int(mutation[col])

            # validate data with samples schema
            if not self.validator.validate_document(sample_obj):
                raise ValueError('%s sample did not pass data validation: %s' % (sample_obj[kn.sample_id_col],
                                                                                 self.validator.errors))

        # insert into mongo
        self.db[s.sample_collection_name].insert_many(clinical_json)

    def _add_genomic_data_to_clinical_dataframe(self, sample_obj):
        """
        Add the genomic data to the "variants" column of the clinical documents

        :param sample_obj: {dict}
        :return: {dict} sample_obj updated with genomic columns
        """
        f1 = (self.p.genomic_df[kn.sample_id_col] == sample_obj[kn.sample_id_col])
        cols = [i for i in self.p.genomic_df.columns if i in s.rename_genomic.values()]
        genomic_json = dataframe_to_json(df=self.p.genomic_df[f1][cols])

        # initialize genomic columns in sample object
        v = VariantsUtils(sample_obj=sample_obj)

        # parse each variant
        for variant_obj in genomic_json:
            if kn.variant_category_col not in variant_obj or \
                    handle_vc(variant_obj[kn.variant_category_col]) not in s.allowed_variants:
                raise ValueError('%s column must be included for each genomic record.' % kn.variant_category_col)

            variant_category = handle_vc(variant_obj[kn.variant_category_col])
            v.variant_parser_dict[variant_category](data=variant_obj)  # todo here

        return v.sample_obj

    def create_clinical_index(self):
        """
        Insert a clinical MongoDB index

        :return: {null}
        """
        raise NotImplementedError
        # logging.info('Creating index...')
        # self.db.genomic.create_index([("TRUE_HUGO_SYMBOL", ASCENDING), ("WILDTYPE", ASCENDING)])
