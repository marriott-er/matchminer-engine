from src.utilities import settings as s
from src.data_store import key_names as kn
from tests.test_match_service import TestQueryUtilitiesShared
from src.services.match_service.query_utils.genomic_queries import GenomicQueries


class TestGenomicQueries(TestQueryUtilitiesShared):
    def setUp(self):
        super(TestGenomicQueries, self).setUp()

        self.gq = GenomicQueries()

    def tearDown(self):
        self.db.testSamples.drop()

    def test_create_gene_level_mutation_query(self):

        # set up
        self.db.testSamples.insert_many([
            self.test_case_braf_v600e,
            self.test_case_braf_non_v600e,
            self.test_case_tp53_r278w
        ])

        # create query
        q1 = self.gq.create_gene_level_query(gene_name='BRAF',
                                             variant_category=s.variant_category_mutation_val,
                                             include=True)
        eq1 = self.gq.create_gene_level_query(gene_name='BRAF',
                                              variant_category=s.variant_category_mutation_val,
                                              include=False)
        res1 = self._findalls(q1)
        eres1 = self._findalls(eq1)
        self._print(q1)
        self._print(eq1)

        # assertions
        assert res1 == ['TEST-SAMPLE-BRAF-NON-V600E', 'TEST-SAMPLE-BRAF-V600E'], res1
        assert eres1 == ['TEST-SAMPLE-TP53-R278W'], eres1

        # clean up
        self.db.testSamples.drop()

    def test_create_variant_level_mutation_query(self):

        # set up
        self.db.testSamples.insert_many([
            self.test_case_braf_v600e,
            self.test_case_braf_non_v600e,
            self.test_case_tp53_r278w,
            self.test_case_erbb2_v600e,
            self.test_case_no_mutation
        ])

        # BRAF V600E (inclusion)
        q1 = self.gq.create_mutation_query(gene_name='BRAF', protein_change='p.V600E', include=True)
        res1 = self._findalls(q1)
        self._print(q1)
        assert res1 == ['TEST-SAMPLE-BRAF-V600E'], res1

        # BRAF V600E (exclusion)
        q2 = self.gq.create_mutation_query(gene_name='BRAF', protein_change='p.V600E', include=False)
        res2 = self._findalls(q2)
        self._print(q2)
        assert res2 == ['TEST-SAMPLE-BRAF-NON-V600E', 'TEST-SAMPLE-ERBB2-V600E',
                        'TEST-SAMPLE-NO-MUTATION', 'TEST-SAMPLE-TP53-R278W'], res2

        # BRAF V600D (inclusion)
        q3 = self.gq.create_mutation_query(gene_name='BRAF', protein_change='p.V600D', include=True)
        res3 = self._findall(q3)
        assert len(res3) == 0, res3

        # BRAF V600D (exclusion)
        q4 = self.gq.create_mutation_query(gene_name='BRAF', protein_change='p.V600D', include=False)
        res4 = self._findalls(q4)
        assert res4 == ['TEST-SAMPLE-BRAF-NON-V600E', 'TEST-SAMPLE-BRAF-V600E', 'TEST-SAMPLE-ERBB2-V600E',
                        'TEST-SAMPLE-NO-MUTATION', 'TEST-SAMPLE-TP53-R278W'], res4

        # clean up
        self.db.testSamples.drop()

    def test_create_wildcard_query(self):

        # set up
        self.db.testSamples.insert_many([
            self.test_case_braf_v600e,
            self.test_case_braf_non_v600e,
            self.test_case_tp53_r278w,
            self.test_case_erbb2_v600e,
            self.test_case_no_mutation
        ])

        # BRAF V600 wildcard (inclusion)
        q1 = self.gq.create_wildcard_query(gene_name='BRAF', protein_change='p.V600', include=True)
        res1 = self._findalls(q1)
        self._print(q1)
        assert res1 == ['TEST-SAMPLE-BRAF-NON-V600E', 'TEST-SAMPLE-BRAF-V600E'], res1

        # BRAF V600 wildcard (exclusion)
        q2 = self.gq.create_wildcard_query(gene_name='BRAF', protein_change='p.V600', include=False)
        res2 = self._findalls(q2)
        self._print(q2)
        assert res2 == ['TEST-SAMPLE-ERBB2-V600E', 'TEST-SAMPLE-NO-MUTATION', 'TEST-SAMPLE-TP53-R278W'], res2

        # clean up
        self.db.testSamples.drop()




    def test_create_gene_level_cnv_query(self):

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
        assert len(res4) == 11, res4
        assert sorted([i[kn.sample_id_col] for i in res4]) == sorted(['TEST-SAMPLE-BRAF-V600E',
                                                                      'TEST-SAMPLE-BRAF-NON-V600E',
                                                                      'TEST-SAMPLE-COLON',
                                                                      'TEST-SAMPLE-LUNG',
                                                                      'TEST-SAMPLE-EGFR',
                                                                      'TEST-SAMPLE-NO-MUTATION',
                                                                      'TEST-SAMPLE-NTRK1-SV',
                                                                      'TEST-SAMPLE-NTRK2-SV',
                                                                      'TEST-SAMPLE-MMR-DEFICIENT',
                                                                      'TEST-SAMPLE-BRAF-WT',
                                                                      'TEST-SAMPLE-BRAF-EXON-20']), res4

    def test_create_gene_level_wt_query(self):

        # BRAF WT (inclusion)
        q5 = self.gq.create_gene_level_query(gene_name='BRAF',
                                             variant_category=s.variant_category_wt_val,
                                             include=True)
        res5 = self._findall(q5)
        assert len(res5) == 1, res5
        assert res5[0][kn.sample_id_col] == 'TEST-SAMPLE-BRAF-WT', res5[0][kn.sample_id_col]

        # BRAF ST (exclusion)
        q6 = self.gq.create_gene_level_query(gene_name='BRAF',
                                             variant_category=s.variant_category_wt_val,
                                             include=False)
        res6 = self._findall(q6)
        assert len(res6) == 13, res6
        assert sorted([i[kn.sample_id_col] for i in res6]) == sorted(['TEST-SAMPLE-BRAF-V600E',
                                                                      'TEST-SAMPLE-BRAF-NON-V600E',
                                                                      'TEST-SAMPLE-COLON',
                                                                      'TEST-SAMPLE-LUNG',
                                                                      'TEST-SAMPLE-EGFR',
                                                                      'TEST-SAMPLE-NO-MUTATION',
                                                                      'TEST-SAMPLE-NTRK1-SV',
                                                                      'TEST-SAMPLE-NTRK2-SV',
                                                                      'TEST-SAMPLE-MMR-DEFICIENT',
                                                                      'TEST-SAMPLE-BRAF-GENERIC-CNV',
                                                                      'TEST-SAMPLE-BRAF-CNV-HETERO-DEL',
                                                                      'TEST-SAMPLE-BRAF-CNV-GAIN',
                                                                      'TEST-SAMPLE-BRAF-EXON-20']), res6


    def test_create_cnv_query(self):

        # BRAF CNV Heterozygous deletion (inclusion)
        q1 = self.gq.create_cnv_query(gene_name='BRAF', cnv_call=s.cnv_call_hetero_del, include=True)
        res1 = self._findall(q1)
        assert len(res1) == 1, res1
        assert res1[0][kn.sample_id_col] == 'TEST-SAMPLE-BRAF-CNV-HETERO-DEL', res1

        # BRAF CNV Heterozygous deletion (exclusion)
        q2 = self.gq.create_cnv_query(gene_name='BRAF', cnv_call=s.cnv_call_hetero_del, include=False)
        res2 = self._findall(q2)
        assert len(res2) == 13, res2
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
                                                                      'TEST-SAMPLE-MMR-DEFICIENT',
                                                                      'TEST-SAMPLE-BRAF-WT',
                                                                      'TEST-SAMPLE-BRAF-EXON-20']), res2


    def test_create_sv_query(self):

        # BRAF SV (inclusion)
        q1 = self.gq.create_sv_query(gene_name='NTRK1', include=True)
        res1 = self._findall(q1)
        assert len(res1) == 1, res1
        assert res1[0][kn.sample_id_col] == 'TEST-SAMPLE-NTRK1-SV', res1

        # BRAF SV (exclusion)
        q2 = self.gq.create_sv_query(gene_name='NTRK1', include=False)
        res2 = self._findall(q2)
        assert len(res2) == 13, res2
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
                                                                      'TEST-SAMPLE-MMR-DEFICIENT',
                                                                      'TEST-SAMPLE-BRAF-WT',
                                                                      'TEST-SAMPLE-BRAF-EXON-20']), res2

    def test_create_mutational_signature_query(self):

        # MMR Deficient (inclusion)
        q1 = self.gq.create_mutational_signature_query(signature_type=kn.mmr_status_col,
                                                       signature_val=s.mmr_status_deficient_val)
        res1 = self._findall(q1)
        assert len(res1) == 1, res1
        assert res1[0][kn.sample_id_col] == 'TEST-SAMPLE-MMR-DEFICIENT', res1

        # MMR Deficient (exclusion)
        q2 = self.gq.create_mutational_signature_query(signature_type=kn.mmr_status_col,
                                                       signature_val=s.mmr_status_proficient_val)
        res2 = self._findall(q2)
        assert len(res2) == 0, res2

    def test_create_exon_query(self):

        # BRAF exon 20 (inclusion)
        q1 = self.gq.create_exon_query(gene_name='BRAF', exon=20, include=True)
        res1 = self._findall(q1)
        assert len(res1) == 1, res1
        assert res1[0][kn.sample_id_col] == 'TEST-SAMPLE-BRAF-EXON-20', res1

        # BRAF exon 20 (exclusion)
        q2 = self.gq.create_exon_query(gene_name='BRAF', exon=20, include=False)
        res2 = self._findall(q2)
        assert len(res2) == 13, res2
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
                                                                      'TEST-SAMPLE-NTRK2-SV',
                                                                      'TEST-SAMPLE-BRAF-WT',
                                                                      'TEST-SAMPLE-MMR-DEFICIENT']), res2

    def test_create_low_coverage_query(self):
        pass
