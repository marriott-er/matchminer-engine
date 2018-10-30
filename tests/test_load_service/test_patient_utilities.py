import os
import unittest

from src.utilities.utilities import get_db
from src.utilities import settings as s
s.MONGO_URI = 'mongodb://localhost:27017'
s.MONGO_DBNAME = 'matchminer'

from src.services.load_service.patient_utilities import PatientUtilities


class TestPatientUtilities(unittest.TestCase):

    def setUp(self):
        super(TestPatientUtilities, self).setUp()

        self.db = get_db(mongo_uri=s.MONGO_URI, mongo_dbname=s.MONGO_DBNAME)
        self.p = PatientUtilities()

        data_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '../', 'data'))
        self.example_clinical_csv = os.path.join(data_path, 'example_clinical.csv')
        self.example_genomic_csv = os.path.join(data_path, 'example_genomic.csv')
        self.example_clinical_pkl = os.path.join(data_path, 'example_clinical.pkl')
        self.example_genomic_pkl = os.path.join(data_path, 'example_genomic.pkl')
        self.example_samples_bson = os.path.join(data_path, 'samples.bson')

        self.clinical_cols = ['MRN', 'sampleId', 'blockNumber', 'dataPushId', 'altMRN', 'patientId',
                              'powerpathPatientId', 'gender', 'firstName', 'lastName', 'birthDate', 'vitalStatus',
                              'firstLast', 'lastFirst', 'diseaseCenterDescr', 'ordPhysicianName', 'ordPhysicianNPI',
                              'ordPhysicianEmail', 'pathologistName', 'lastVisitDate', 'panelVersion', 'reportComment',
                              'dateReceivedAtSeqCenter', 'reportDate', 'reportVersion', 'testType', 'qcResult',
                              'cnvResults', 'snvResults', 'cancerTypePercentile', 'allProfilePercentil',
                              'metamainCount', 'caseCount', 'pdfLayoutVersion', 'referenceGenome', 'totalAlignedReads',
                              'pctTargetBase', 'meanSampleCoverage', 'totalReads', 'tumorMutationalBurdenPerMegabase',
                              'oncotreePrimaryDiagnosis', 'oncotreePrimaryDiagnosisName', 'tumorPurityPercent',
                              'oncotreeBiopsySite', 'oncotreeBiopsySiteType', 'oncotreeBiopsySiteName',
                              'oncotreeBiopsySiteMeta', 'oncotreeBiopsySiteColor', 'oncotreePrimaryDiagnosisMeta',
                              'oncotreePrimaryDiagnosisColor', 'question1Consent', 'question2Consent',
                              'question3Consent', 'question4Consent', 'question5Consent', 'crisConsent', 'consent17000']

        self.genomic_cols = ['sampleId', 'wildtype', 'variantCategory', 'trueVariantClassification', 'chromosome',
                             'position', 'trueStrand', 'trueTranscriptExon', 'trueHugoSymbol', 'trueProteinChange',
                             'trueCDNAChange', 'treuCDNATranscriptId', 'alternateAllele', 'referenceAllele',
                             'alleleFraction', 'tier', 'cytoband', 'cnvCall', 'cnvBand', 'cnvHugoSymbol', 'copyCount',
                             'cnvRowId', 'actionability', 'structuralVariantComment', 'mmrStatus', 'tobaccoStatus',
                             'tmzStatus', 'polEStatus', 'apobecStatus', 'uvaStatus', 'trueEntrezId',
                             'besteffectCDNAChange', 'besteffectCDNATranscriptId', 'besteffectEntrezId',
                             'besteffectHugoSymbol', 'besteffectProteinChange', 'besteffectTranscriptExon',
                             'besteffectVariantClassification', 'canonicalCDNAChange', 'canonicalCDNATranscriptId',
                             'canonicalEntrezId', 'canonicalHugoSymbol', 'canonicalProteinChange', 'canonicalStrand',
                             'canonicalTranscriptExon', 'canonicalVariantClassification', 'coverage',
                             'transcriptSource', 'somaticStatus']

    def tearDown(self):
        self.db.samples.drop()

    def test_load_csv(self):

        self.p.load_csv(clinical=self.example_clinical_csv, genomic=self.example_genomic_csv)

        assert self.p.clinical_df.columns.tolist() == self.clinical_cols
        assert len(self.p.clinical_df.index) == 1

        assert self.p.genomic_df.columns.tolist() == self.genomic_cols
        assert len(self.p.genomic_df.index) == 11

    def test_load_pkl(self):

        self.p.load_pkl(clinical=self.example_clinical_pkl, genomic=self.example_genomic_pkl)

        assert self.p.clinical_df.columns.tolist() == self.clinical_cols
        assert len(self.p.clinical_df.index) == 1

        assert self.p.genomic_df.columns.tolist() == self.genomic_cols
        assert len(self.p.genomic_df.index) == 11

    def test_load_bson(self):

        self.p.load_bson(samples_bson=self.example_samples_bson)
        samples = list(self.db.samples.find())
        assert samples is not None
        assert len(samples) == 2
