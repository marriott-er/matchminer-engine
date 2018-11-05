from src.data_store import key_names as kn
from tests.test_match_service import TestQueryUtilitiesShared
from src.services.match_service.query_utilities.genomic_queries import GenomicQueries


class TestGenomicQueries(TestQueryUtilitiesShared):
    def setUp(self):
        super(TestGenomicQueries, self).setUp()

        self.gq = GenomicQueries()
        self.db.testSamples.insert_many(self.test_cases)

    def tearDown(self):
        self.db.testSamples.drop()

    def test_create_gene_level_query(self):

        q1 = self.gq.create_gene_level_query(gene_name='BRAF', include=True)
        q2 = self.gq.create_gene_level_query(gene_name='BRAF', include=False)
        res1 = self._findall(q1)
        res2 = self._findall(q2)

        assert len(res1) == 2, res1
        assert sorted([i[kn.sample_id_col] for i in res1]) == sorted(['TEST-SAMPLE-BRAF-V600E',
                                                                      'TEST-SAMPLE-BRAF-NON-V600E']), res2

        assert len(res2) == 2, res2
        assert sorted([i[kn.sample_id_col] for i in res2]) == sorted(['TEST-SAMPLE-EGFR',
                                                                      'TEST-SAMPLE-NO-MUTATION']), res2

    def test_create_variant_level_snv_missense_query(self):

        q1 = self.gq.create_variant_level_snv_missense_query(gene_name='BRAF', protein_change='p.V600E', include=True)
        q2 = self.gq.create_variant_level_snv_missense_query(gene_name='BRAF', protein_change='p.V600E', include=False)
        q3 = self.gq.create_variant_level_snv_missense_query(gene_name='BRAF', protein_change='p.V600D', include=True)
        q4 = self.gq.create_variant_level_snv_missense_query(gene_name='BRAF', protein_change='p.V600D', include=False)
        res1 = self._findall(q1)
        res2 = self._findall(q2)
        res3 = self._findall(q3)
        res4 = self._findall(q4)

        assert len(res1) == 1, res1
        assert res1[0][kn.sample_id_col] == 'TEST-SAMPLE-BRAF-V600E', res1
        assert len(res2) == 3, res2
        assert sorted([i[kn.sample_id_col] for i in res2]) == sorted(['TEST-SAMPLE-BRAF-NON-V600E',
                                                                      'TEST-SAMPLE-EGFR',
                                                                      'TEST-SAMPLE-NO-MUTATION']), res2
        assert len(res3) == 0, res3
        assert len(res4) == 4, res4
        assert sorted([i[kn.sample_id_col] for i in res4]) == sorted(['TEST-SAMPLE-BRAF-V600E',
                                                                      'TEST-SAMPLE-BRAF-NON-V600E',
                                                                      'TEST-SAMPLE-EGFR',
                                                                      'TEST-SAMPLE-NO-MUTATION']), res4

    def create_cnv_query(self):
        raise NotImplementedError

    def create_sv_query(self):
        raise NotImplementedError

    def create_mutational_signature_query(self):
        raise NotImplementedError

    def create_wildtype_query(self):
        raise NotImplementedError

    def create_wildcard_query(self):
        raise NotImplementedError

    def create_exon_query(self):
        raise NotImplementedError

    def create_low_coverage_query(self):
        raise NotImplementedError
