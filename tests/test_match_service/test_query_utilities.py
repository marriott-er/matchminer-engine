import unittest

from src.utilities import settings as s
s.MONGO_URI = 'mongodb://localhost:27017'
s.MONGO_DBNAME = 'matchminer'

from src.utilities.utilities import get_db
from tests.test_match_service import *
from src.services.match_service.query_utilities import QueryUtilities


class TestQueryUtilities(unittest.TestCase):

    def setUp(self):
        super(TestQueryUtilities, self).setUp()

        self.q = QueryUtilities()
        self.db = get_db(mongo_uri=s.MONGO_URI, mongo_dbname=s.MONGO_DBNAME)
        self.proj = {kn.sample_id_col: 1}

        test_cases = [test_case_lung, test_case_colon]
        self.db.testSamples.insert_many(test_cases)

    def tearDown(self):
        self.db.testSamples.drop()

    def _find(self, query):
        return self.db.testSamples.find_one(query, self.proj)

    def test_create_oncotree_diagnosis_query(self):

        q1 = self.q.create_oncotree_diagnosis_query(cancer_type='Lung', include=True)
        q2 = self.q.create_oncotree_diagnosis_query(cancer_type='Lung', include=False)
        res1 = self._find(q1)
        res2 = self._find(q2)

        assert res1 is not None
        assert res2 is not None
        assert res1[kn.sample_id_col] == 'TEST-SAMPLE-LUNG', res1
        assert res2[kn.sample_id_col] == 'TEST-SAMPLE-COLON', res2

    def test_create_age_query(self):
        raise NotImplementedError

    def test_create_gene_level_query(self):

        q1 = self.q.create_gene_level_query(gene_name='BRAF', variant_category='MUTATION', include=True)
        q2 = self.q.create_gene_level_query(gene_name='BRAF', variant_category='MUTATION', include=False)
        q3 = self.q.create_gene_level_query(gene_name='BRAF', variant_category='CNV', include=True)
        q4 = self.q.create_gene_level_query(gene_name='BRAF', variant_category='CNV', include=False)

        assert q1 == {'variants.snvs.BRAF.variantCategory': {'$eq': 'MUTATION'}}, q1
        assert q2 == {'variants.snvs.BRAF.variantCategory': {'$ne': 'MUTATION'}}, q2
        assert q3 == {'variants.snvs.BRAF.variantCategory': {'$eq': 'CNV'}}, q3
        assert q4 == {'variants.snvs.BRAF.variantCategory': {'$ne': 'CNV'}}, q4

    def test_create_variant_level_snv_missense_query(self):

        q1 = self.q.create_variant_level_snv_missense_query(gene_name='BRAF', protein_change='p.V600E', include=True)
        q2 = self.q.create_variant_level_snv_missense_query(gene_name='BRAF', protein_change='p.V600E', include=False)

        assert q1 == {'variants.snvs.BRAF.trueProteinChange': {'$eq': 'p.V600E'}}, q1
        assert q2 == {'variants.snvs.BRAF.trueProteinChange': {'$ne': 'p.V600E'}}, q2

    def test_create_variant_level_cnv_query(self):

        q1 = self.q.create_variant_level_cnv_query(gene_name='BRAF', cnv_call='Heterozygous deletion', include=True)
        q2 = self.q.create_variant_level_cnv_query(gene_name='BRAF', cnv_call='Heterozygous deletion', include=False)

        assert q1 == {'variants.cnvs.BRAF.cnvCall': {'$eq': 'Heterozygous deletion'}}, q1
        assert q2 == {'variants.cnvs.BRAF.cnvCall': {'$ne': 'Heterozygous deletion'}}, q2

    def test_create_sv_query(self):

        q1 = self.q.create_sv_query(gene_name='BRAF', include=True)
        q2 = self.q.create_sv_query(gene_name='BRAF', include=False)

        assert q1 == {'variants.svs.structuralVariantComment': {'$eq': {'$regex': 'BRAF'}}}, q1
        assert q2 == {'variants.svs.structuralVariantComment': {'$ne': {'$regex': 'BRAF'}}}, q2

    def test_create_mutational_signature_query(self):

        q1 = self.q.create_mutational_signature_query(signature_type='mmrStatus',
                                                      signature_val='Deficient (MMR-D / MSI-H)',
                                                      include=True)
        q2 = self.q.create_mutational_signature_query(signature_type='mmrStatus',
                                                      signature_val='Deficient (MMR-D / MSI-H)',
                                                      include=False)
        q3 = self.q.create_mutational_signature_query(signature_type='tobaccoStatus', signature_val='No', include=True)
        q4 = self.q.create_mutational_signature_query(signature_type='tobaccoStatus', signature_val='No', include=False)
        q5 = self.q.create_mutational_signature_query(signature_type='tmzStatus', signature_val='No', include=True)
        q6 = self.q.create_mutational_signature_query(signature_type='tmzStatus',signature_val='No', include=False)
        q7 = self.q.create_mutational_signature_query(signature_type='polEStatus', signature_val='No', include=True)
        q8 = self.q.create_mutational_signature_query(signature_type='polEStatus', signature_val='No', include=False)
        q9 = self.q.create_mutational_signature_query(signature_type='apobecStatus', signature_val='No', include=True)
        q10 = self.q.create_mutational_signature_query(signature_type='apobecStatus', signature_val='No', include=False)
        q11 = self.q.create_mutational_signature_query(signature_type='uvaStatus', signature_val='No', include=True)
        q12 = self.q.create_mutational_signature_query(signature_type='uvaStatus', signature_val='No', include=False)

        assert q1 == {'variants.signatures.mmrStatus': {'$eq': 'Deficient (MMR-D / MSI-H)'}}, q1
        assert q2 == {'variants.signatures.mmrStatus': {'$ne': 'Deficient (MMR-D / MSI-H)'}}, q2
        assert q3 == {'variants.signatures.tobaccoStatus': {'$eq': 'No'}}, q3
        assert q4 == {'variants.signatures.tobaccoStatus': {'$ne': 'No'}}, q4
        assert q5 == {'variants.signatures.tmzStatus': {'$eq': 'No'}}, q5
        assert q6 == {'variants.signatures.tmzStatus': {'$ne': 'No'}}, q6
        assert q7 == {'variants.signatures.polEStatus': {'$eq': 'No'}}, q7
        assert q8 == {'variants.signatures.polEStatus': {'$ne': 'No'}}, q8
        assert q9 == {'variants.signatures.apobecStatus': {'$eq': 'No'}}, q9
        assert q10 == {'variants.signatures.apobecStatus': {'$ne': 'No'}}, q10
        assert q11 == {'variants.signatures.uvaStatus': {'$eq': 'No'}}, q11
        assert q12 == {'variants.signatures.uvaStatus': {'$ne': 'No'}}, q12

    def test_create_wild_type_query(self):

        q1 = self.q.create_wild_type_query(gene_name='BRAF')
        assert q1 == {
            '$and': [
                {'variants.snvs.BRAF': {'$exists': False}},
                {'variants.cnvs.BRAF': {'$exists': False}}
            ]
        }
