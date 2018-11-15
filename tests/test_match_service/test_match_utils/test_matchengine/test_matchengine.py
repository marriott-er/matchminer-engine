from src.utilities import settings as s
from src.data_store import key_names as kn
from tests.test_match_service import TestQueryUtilitiesShared
from src.services.match_service.match_utils.trial_utils import TrialUtils
from src.services.match_service.match_utils.matchengine.matchengine import MatchEngine

import datetime as dt


class TestMatchEngine(TestQueryUtilitiesShared):

    def setUp(self):
        super(TestMatchEngine, self).setUp()

        self.db.testSamples.insert_many(self.test_cases)

    def tearDown(self):
        self.db.testSamples.drop()
        self.db[s.sample_collection_name].drop()

    @staticmethod
    def _set_up_matchengine(trial):
        t = TrialUtils(trial=trial)
        return t.parse_match_trees_from_trial()[0]

    def test_complex_conversion(self):

        # set up matching records
        doc1 = {
            kn.sample_id_col: 'DEV-01',
            kn.mrn_col: '01',
            kn.vital_status_col: 'alive',
            kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
            kn.birth_date_col: dt.datetime(year=1900, day=1, month=1),
            kn.mutation_list_col: [
                {kn.hugo_symbol_col: 'EGFR', kn.transcript_exon_col: 19, kn.variant_class_col: 'In_Frame_Del'}
            ]
        }  # (y)
        doc2 = {
            kn.sample_id_col: 'DEV-02',
            kn.mrn_col: '01',
            kn.vital_status_col: 'alive',
            kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
            kn.birth_date_col: dt.datetime(year=1900, day=1, month=1),
            kn.mutation_list_col: [
                {
                    kn.hugo_symbol_col: 'EGFR',
                    kn.variant_category_col: s.variant_category_mutation_val,
                    kn.protein_change_col: 'p.XXXX'
                },
                {
                    kn.hugo_symbol_col: 'EGFR',
                    kn.variant_category_col: s.variant_category_mutation_val,
                    kn.protein_change_col: 'p.E709K'
                }
            ]
        }  # (y)
        doc3 = {
            kn.sample_id_col: 'DEV-03',
            kn.mrn_col: '01',
            kn.vital_status_col: 'alive',
            kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
            kn.birth_date_col: dt.datetime(year=1900, day=1, month=1),
            kn.mutation_list_col: [
                {
                    kn.hugo_symbol_col: 'EGFR',
                    kn.variant_category_col: s.variant_category_mutation_val,
                    kn.protein_change_col: 'p.XXXX'
                },
                {
                    kn.hugo_symbol_col: 'EGFR',
                    kn.variant_category_col: s.variant_category_mutation_val,
                    kn.protein_change_col: 'p.E709K'
                }
            ],
            kn.sv_list_col: [{kn.sv_comment_col: 'This contains an ALK SV'}]
        }  # (n)
        doc4 = {
            kn.sample_id_col: 'DEV-04',
            kn.mrn_col: '01',
            kn.vital_status_col: 'alive',
            kn.oncotree_primary_diagnosis_name_col: 'Melanoma',
            kn.birth_date_col: dt.datetime(year=1900, day=1, month=1),
            kn.mutation_list_col: [
                {
                    kn.hugo_symbol_col: 'EGFR',
                    kn.variant_category_col: s.variant_category_mutation_val,
                    kn.protein_change_col: 'p.XXXX'
                },
                {
                    kn.hugo_symbol_col: 'EGFR',
                    kn.variant_category_col: s.variant_category_mutation_val,
                    kn.protein_change_col: 'p.E709K'
                }
            ]
        }  # (n)
        doc5 = {
            kn.sample_id_col: 'DEV-05',
            kn.mrn_col: '01',
            kn.vital_status_col: 'alive',
            kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
            kn.birth_date_col: dt.datetime(year=1900, day=1, month=1),
            kn.mutation_list_col: [
                {
                    kn.hugo_symbol_col: 'EGFR',
                    kn.variant_category_col: s.variant_category_mutation_val,
                    kn.protein_change_col: 'p.L833V'
                },
                {
                    kn.hugo_symbol_col: 'EGFR',
                    kn.variant_category_col: s.variant_category_mutation_val,
                    kn.protein_change_col: 'p.E709K'
                },
                {
                    kn.hugo_symbol_col: 'BRAF',
                    kn.variant_category_col: s.variant_category_mutation_val,
                    kn.protein_change_col: 'p.V600D'
                }
            ]
        }  # (y)
        doc6 = {
            kn.sample_id_col: 'DEV-06',
            kn.mrn_col: '01',
            kn.vital_status_col: 'alive',
            kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
            kn.birth_date_col: dt.datetime(year=1900, day=1, month=1),
            kn.mutation_list_col: [
                {
                    kn.hugo_symbol_col: 'EGFR',
                    kn.variant_category_col: s.variant_category_mutation_val,
                    kn.protein_change_col: 'p.XXXX'
                },
                {
                    kn.hugo_symbol_col: 'EGFR',
                    kn.variant_category_col: s.variant_category_mutation_val,
                    kn.protein_change_col: 'p.E709K'
                },
                {
                    kn.hugo_symbol_col: 'BRAF',
                    kn.variant_category_col: s.variant_category_mutation_val,
                    kn.protein_change_col: 'p.V600E'
                }
            ]
        }  # (y)

        self.db[s.sample_collection_name].insert_many([doc1, doc2, doc3, doc4, doc5, doc6])

        # find matches
        me = MatchEngine(match_tree=self.complex_match_tree, trial_info={})
        me.convert_match_tree_to_digraph()
        me.traverse_match_tree()
        self._print(me.matches)
        assert sorted(list(set([i[kn.sample_id_col] for i in me.matches]))) == ['DEV-01', 'DEV-02', 'DEV-05'], \
            sorted([i[kn.sample_id_col] for i in me.matches])

    def test_combination_match(self):

        # set up matching records
        doc1 = {
            kn.sample_id_col: 'DEV-01',
            kn.mrn_col: '01',
            kn.vital_status_col: 'alive',
            kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
            kn.birth_date_col: dt.datetime(year=1900, day=1, month=1),
            kn.mutation_list_col: [
                {
                    kn.hugo_symbol_col: 'EGFR',
                    kn.variant_category_col: s.variant_category_mutation_val,
                    kn.protein_change_col: 'p.E709K'
                },
                {
                    kn.hugo_symbol_col: 'BRAF',
                    kn.variant_category_col: s.variant_category_mutation_val,
                    kn.protein_change_col: 'p.V600E'
                }
            ]
        }
        doc2 = {
            kn.sample_id_col: 'DEV-02',
            kn.mrn_col: '01',
            kn.vital_status_col: 'alive',
            kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
            kn.birth_date_col: dt.datetime(year=1900, day=1, month=1),
            kn.mutation_list_col: [
                {
                    kn.hugo_symbol_col: 'BRAF',
                    kn.variant_category_col: s.variant_category_mutation_val,
                    kn.protein_change_col: 'p.V600E'
                }
            ]
        }
        doc3 = {
            kn.sample_id_col: 'DEV-03',
            kn.mrn_col: '01',
            kn.vital_status_col: 'alive',
            kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
            kn.birth_date_col: dt.datetime(year=1900, day=1, month=1),
            kn.mutation_list_col: [
                {
                    kn.hugo_symbol_col: 'EGFR',
                    kn.variant_category_col: s.variant_category_mutation_val,
                    kn.protein_change_col: 'p.E709K'
                }
            ]
        }

        self.db[s.sample_collection_name].insert_many([doc1, doc2, doc3])

        # find matches
        me = MatchEngine(match_tree=self.simple_and_tree, trial_info={})
        me.convert_match_tree_to_digraph()
        me.traverse_match_tree()
        print '---AND---'
        self._print(me.matches)

        me = MatchEngine(match_tree=self.simple_or_tree, trial_info={})
        me.convert_match_tree_to_digraph()
        me.traverse_match_tree()
        print '\n---OR---'
        self._print(me.matches)

        me = MatchEngine(match_tree=self.complex_or_tree, trial_info={})
        me.convert_match_tree_to_digraph()
        me.traverse_match_tree()
        print '\n---COMPLEX OR---'
        self._print(me.matches)

    def test_convert_match_tree_to_digraph(self):

        me = MatchEngine(match_tree=self.simple_mutation_match_tree, trial_info={})
        me.convert_match_tree_to_digraph()
        assert me.match_tree_nx is not None
        assert me.match_tree_nx.node[1] == {'type': 'and'}
        assert me.match_tree_nx.node[2] == {'type': 'genomic', 'value': self.simple_mutation_match_tree['and'][0]['genomic']}
        assert me.match_tree_nx.node[3] == {'type': 'clinical', 'value': self.simple_mutation_match_tree['and'][1]['clinical']}

    def test_search_for_matching_records(self):

        self.db[s.sample_collection_name].insert_many([
            self.test_case_lung,
            self.test_case_colon,
            self.test_case_braf_v600e
        ])

        # clinical inclusion
        node = {
            'type': 'clinical',
            'query': {kn.oncotree_primary_diagnosis_name_col: 'Lung'},
            'clinical_inclusion_reasons': {
                '_id': 0, kn.sample_id_col: 1,
                kn.oncotree_primary_diagnosis_name_col: 1
            }
        }
        me = MatchEngine(match_tree=None, trial_info=None)
        m = me._search_for_matching_records(node=node)
        assert m == [{
            kn.sample_id_col: 'TEST-SAMPLE-LUNG',
            kn.oncotree_primary_diagnosis_name_col: 'Lung'
        }], m

        # clinical exclusion
        node = {
            'type': 'clinical',
            'query': {kn.oncotree_primary_diagnosis_name_col: {'$ne': 'Lung'}},
            'clinical_exclusion_reasons': {kn.oncotree_primary_diagnosis_name_col: 'Lung'}
        }
        me = MatchEngine(match_tree=None, trial_info=None)
        m = me._search_for_matching_records(node=node)
        assert m[0] == {
            kn.sample_id_col: 'TEST-SAMPLE-COLON',
            'clinical_exclusion_reasons': [{
                kn.oncotree_primary_diagnosis_name_col: 'Lung'
            }]
        }, m[0]

        # genomic inclusion
        node = {
            'type': 'genomic',
            'query': {kn.mutation_list_col: {'$elemMatch': {kn.hugo_symbol_col: 'BRAF'}}},
            'variant_level': 'gene',
            'genomic_inclusion_reasons': {
                '_id': 0, kn.sample_id_col: 1,
                kn.oncotree_primary_diagnosis_name_col: 1,
                kn.mutation_list_col: {'$elemMatch': {kn.hugo_symbol_col: 'BRAF'}}
            }
        }
        me = MatchEngine(match_tree=None, trial_info=None)
        m = me._search_for_matching_records(node=node)
        assert m == [{
            kn.sample_id_col: 'TEST-SAMPLE-BRAF-V600E',
            kn.oncotree_primary_diagnosis_name_col: 'Breast',
            kn.mutation_list_col: [{
                kn.mr_inclusion_criteria_col: True,
                kn.mr_reason_level_col: 'gene',
                kn.hugo_symbol_col: 'BRAF',
                kn.protein_change_col: 'p.V600E',
                kn.ref_residue_col: 'p.V600'
            }]
        }], m

        # genomic exclusion
        node = {
            'type': 'genomic',
            'query': {kn.mutation_list_col: {'$not': {'$elemMatch': {kn.hugo_symbol_col: 'BRAF'}}}},
            'variant_level': 'gene',
            'genomic_exclusion_reasons': {
                kn.hugo_symbol_col: 'BRAF',
                kn.mutation_list_col: s.variant_category_mutation_val
            }
        }
        me = MatchEngine(match_tree=None, trial_info=None)
        m = me._search_for_matching_records(node=node)
        assert m[1] == {
            kn.sample_id_col: 'TEST-SAMPLE-COLON',
            'genomic_exclusion_reasons': [{
                kn.hugo_symbol_col: 'BRAF',
                kn.mutation_list_col: s.variant_category_mutation_val
            }]
        }, m[1]
