from src.utilities import settings as s
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

        # BRAF Mutation (inclusion)
        q1 = self.gq.create_gene_level_query(gene_name='BRAF',
                                             variant_category=s.variant_category_mutation_val,
                                             include=True)
        res1 = self._findall(q1)
        assert len(res1) == 2, res1
        assert sorted([i[kn.sample_id_col] for i in res1]) == sorted(['TEST-SAMPLE-BRAF-V600E',
                                                                      'TEST-SAMPLE-BRAF-NON-V600E']), res1

        # BRAF Mutation (exclusion)
        q2 = self.gq.create_gene_level_query(gene_name='BRAF',
                                             variant_category=s.variant_category_mutation_val,
                                             include=False)
        res2 = self._findall(q2)
        assert len(res2) == 10, res2
        assert sorted([i[kn.sample_id_col] for i in res2]) == sorted(['TEST-SAMPLE-COLON',
                                                                      'TEST-SAMPLE-LUNG',
                                                                      'TEST-SAMPLE-EGFR',
                                                                      'TEST-SAMPLE-NO-MUTATION',
                                                                      'TEST-SAMPLE-BRAF-GENERIC-CNV',
                                                                      'TEST-SAMPLE-BRAF-CNV-HETERO-DEL',
                                                                      'TEST-SAMPLE-BRAF-CNV-GAIN',
                                                                      'TEST-SAMPLE-NTRK1-SV',
                                                                      'TEST-SAMPLE-NTRK2-SV',
                                                                      'TEST-SAMPLE-MMR-DEFICIENT']), res2

        # BRAF any CNV (inclusion)
        q3 = self.gq.create_gene_level_query(gene_name='BRAF',
                                             variant_category=s.variant_category_cnv_val,
                                             include=True)
        res3 = self._findall(q3)
        assert len(res3) == 3, res3
        assert sorted([i[kn.sample_id_col] for i in res3]) == sorted(['TEST-SAMPLE-BRAF-GENERIC-CNV',
                                                                      'TEST-SAMPLE-BRAF-CNV-HETERO-DEL',
                                                                      'TEST-SAMPLE-BRAF-CNV-GAIN']), res3

        # BRAF any CNV (exclusion)
        q4 = self.gq.create_gene_level_query(gene_name='BRAF',
                                             variant_category=s.variant_category_cnv_val,
                                             include=False)
        res4 = self._findall(q4)
        assert len(res4) == 9, res4
        assert sorted([i[kn.sample_id_col] for i in res4]) == sorted(['TEST-SAMPLE-BRAF-V600E',
                                                                      'TEST-SAMPLE-BRAF-NON-V600E',
                                                                      'TEST-SAMPLE-COLON',
                                                                      'TEST-SAMPLE-LUNG',
                                                                      'TEST-SAMPLE-EGFR',
                                                                      'TEST-SAMPLE-NO-MUTATION',
                                                                      'TEST-SAMPLE-NTRK1-SV',
                                                                      'TEST-SAMPLE-NTRK2-SV',
                                                                      'TEST-SAMPLE-MMR-DEFICIENT']), res4

    def test_create_variant_level_snv_missense_query(self):

        # BRAF V600E (inclusion)
        q1 = self.gq.create_variant_level_snv_missense_query(gene_name='BRAF', protein_change='p.V600E', include=True)
        res1 = self._findall(q1)
        assert len(res1) == 1, res1
        assert res1[0][kn.sample_id_col] == 'TEST-SAMPLE-BRAF-V600E', res1

        # BRAF V600E (exclusion)
        q2 = self.gq.create_variant_level_snv_missense_query(gene_name='BRAF', protein_change='p.V600E', include=False)
        res2 = self._findall(q2)
        assert len(res2) == 11, res2
        assert sorted([i[kn.sample_id_col] for i in res2]) == sorted(['TEST-SAMPLE-BRAF-NON-V600E',
                                                                      'TEST-SAMPLE-EGFR',
                                                                      'TEST-SAMPLE-NO-MUTATION',
                                                                      'TEST-SAMPLE-COLON',
                                                                      'TEST-SAMPLE-LUNG',
                                                                      'TEST-SAMPLE-BRAF-GENERIC-CNV',
                                                                      'TEST-SAMPLE-BRAF-CNV-HETERO-DEL',
                                                                      'TEST-SAMPLE-BRAF-CNV-GAIN',
                                                                      'TEST-SAMPLE-NTRK1-SV',
                                                                      'TEST-SAMPLE-NTRK2-SV',
                                                                      'TEST-SAMPLE-MMR-DEFICIENT']), res2

        # BRAF V600D (inclusion)
        q3 = self.gq.create_variant_level_snv_missense_query(gene_name='BRAF', protein_change='p.V600D', include=True)
        res3 = self._findall(q3)
        assert len(res3) == 0, res3

        # BRAF V600D (exclusion)
        q4 = self.gq.create_variant_level_snv_missense_query(gene_name='BRAF', protein_change='p.V600D', include=False)
        res4 = self._findall(q4)
        assert len(res4) == 12, res4
        assert sorted([i[kn.sample_id_col] for i in res4]) == sorted(['TEST-SAMPLE-BRAF-V600E',
                                                                      'TEST-SAMPLE-BRAF-NON-V600E',
                                                                      'TEST-SAMPLE-EGFR',
                                                                      'TEST-SAMPLE-NO-MUTATION',
                                                                      'TEST-SAMPLE-COLON',
                                                                      'TEST-SAMPLE-LUNG',
                                                                      'TEST-SAMPLE-BRAF-GENERIC-CNV',
                                                                      'TEST-SAMPLE-BRAF-CNV-HETERO-DEL',
                                                                      'TEST-SAMPLE-BRAF-CNV-GAIN',
                                                                      'TEST-SAMPLE-NTRK1-SV',
                                                                      'TEST-SAMPLE-NTRK2-SV',
                                                                      'TEST-SAMPLE-MMR-DEFICIENT']), res4

    def test_create_cnv_query(self):

        # BRAF CNV Heterozygous deletion (inclusion)
        q1 = self.gq.create_cnv_query(gene_name='BRAF', cnv_call=s.cnv_call_hetero_del, include=True)
        res1 = self._findall(q1)
        assert len(res1) == 1, res1
        assert res1[0][kn.sample_id_col] == 'TEST-SAMPLE-BRAF-CNV-HETERO-DEL', res1

        # BRAF CNV Heterozygous deletion (exclusion)
        q2 = self.gq.create_cnv_query(gene_name='BRAF', cnv_call=s.cnv_call_hetero_del, include=False)
        res2 = self._findall(q2)
        assert len(res2) == 11, res2
        assert sorted([i[kn.sample_id_col] for i in res2]) == sorted(['TEST-SAMPLE-BRAF-V600E',
                                                                      'TEST-SAMPLE-BRAF-NON-V600E',
                                                                      'TEST-SAMPLE-EGFR',
                                                                      'TEST-SAMPLE-NO-MUTATION',
                                                                      'TEST-SAMPLE-COLON',
                                                                      'TEST-SAMPLE-LUNG',
                                                                      'TEST-SAMPLE-BRAF-GENERIC-CNV',
                                                                      'TEST-SAMPLE-BRAF-CNV-GAIN',
                                                                      'TEST-SAMPLE-NTRK1-SV',
                                                                      'TEST-SAMPLE-NTRK2-SV',
                                                                      'TEST-SAMPLE-MMR-DEFICIENT']), res2

    def test_create_sv_query(self):

        # BRAF SV (inclusion)
        q1 = self.gq.create_sv_query(gene_name='NTRK1', include=True)
        res1 = self._findall(q1)
        assert len(res1) == 1, res1
        assert res1[0][kn.sample_id_col] == 'TEST-SAMPLE-NTRK1-SV', res1

        # BRAF SV (exclusion)
        q2 = self.gq.create_sv_query(gene_name='NTRK1', include=False)
        res2 = self._findall(q2)
        assert len(res2) == 11, res2
        assert sorted([i[kn.sample_id_col] for i in res2]) == sorted(['TEST-SAMPLE-BRAF-V600E',
                                                                      'TEST-SAMPLE-BRAF-NON-V600E',
                                                                      'TEST-SAMPLE-EGFR',
                                                                      'TEST-SAMPLE-NO-MUTATION',
                                                                      'TEST-SAMPLE-COLON',
                                                                      'TEST-SAMPLE-LUNG',
                                                                      'TEST-SAMPLE-BRAF-GENERIC-CNV',
                                                                      'TEST-SAMPLE-BRAF-CNV-GAIN',
                                                                      'TEST-SAMPLE-BRAF-CNV-HETERO-DEL',
                                                                      'TEST-SAMPLE-NTRK2-SV',
                                                                      'TEST-SAMPLE-MMR-DEFICIENT']), res2

    def test_create_mutational_signature_query(self):

        # MMR Deficient (inclusion)
        q1 = self.gq.create_mutational_signature_query(signature_type=kn.mmr_status_col,
                                                       signature_val=s.mmr_status_deficient_val,
                                                       include=True)
        res1 = self._findall(q1)
        assert len(res1) == 1, res1
        assert res1[0][kn.sample_id_col] == 'TEST-SAMPLE-MMR-DEFICIENT', res1

        # MMR Deficient (exclusion)
        q2 = self.gq.create_mutational_signature_query(signature_type=kn.mmr_status_col,
                                                       signature_val=s.mmr_status_deficient_val,
                                                       include=False)
        res2 = self._findall(q2)
        assert len(res2) == 11, res2
        assert sorted([i[kn.sample_id_col] for i in res2]) == sorted(['TEST-SAMPLE-BRAF-V600E',
                                                                      'TEST-SAMPLE-BRAF-NON-V600E',
                                                                      'TEST-SAMPLE-EGFR',
                                                                      'TEST-SAMPLE-NO-MUTATION',
                                                                      'TEST-SAMPLE-COLON',
                                                                      'TEST-SAMPLE-LUNG',
                                                                      'TEST-SAMPLE-BRAF-GENERIC-CNV',
                                                                      'TEST-SAMPLE-BRAF-CNV-GAIN',
                                                                      'TEST-SAMPLE-BRAF-CNV-HETERO-DEL',
                                                                      'TEST-SAMPLE-NTRK1-SV',
                                                                      'TEST-SAMPLE-NTRK2-SV']), res2

    def test_create_wildtype_query(self):
        raise NotImplementedError

    def test_create_wildcard_query(self):
        raise NotImplementedError

    def test_create_exon_query(self):
        raise NotImplementedError

    def test_create_low_coverage_query(self):
        raise NotImplementedError
