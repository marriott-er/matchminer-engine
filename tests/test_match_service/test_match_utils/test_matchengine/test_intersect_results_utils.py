from src.utilities import settings as s
from src.data_store import key_names as kn
from tests.test_match_service import TestQueryUtilitiesShared
from src.services.match_service.match_utils.matchengine.intersect_results_utils import IntersectResultsUtils


class TestIntersectResultsUtils(TestQueryUtilitiesShared):

    def setUp(self):
        super(TestIntersectResultsUtils, self).setUp()

        self.i = IntersectResultsUtils()

    def tearDown(self):
        pass

    def test_get_sample_ids(self):

        node = {'matches': [
            {kn.sample_id_col: 'DEV1'},
            {kn.sample_id_col: 'DEV2'}
        ]}
        res = self.i._get_sample_ids(node)
        assert sorted(res) == ['DEV1', 'DEV2'], res

    def test_filter_matches(self):

        sample_ids = ['DEV1', 'DEV3']
        node = {'matches': [
            {kn.sample_id_col: 'DEV1'},
            {kn.sample_id_col: 'DEV2'}
        ]}
        res = self.i._filter_matches(node=node, sample_ids=sample_ids)
        assert sorted(res) == [{kn.sample_id_col: 'DEV1'}], res

    def test_update_old_match(self):

        keys = ['key1', 'key2']
        old_match = {'key0': 0}
        child_match = {'key1': 1}
        res = self.i._update_old_match(old_match, child_match, keys)
        assert res == {'key0': 0, 'key1': 1}, res

        old_match = {'key1': 1}
        child_match = {'key1': 1}
        res = self.i._update_old_match(old_match, child_match, keys)
        assert res == {'key1': 1}, res

        old_match = {'key1': {'one': 1}}
        child_match = {'key1': {'two': 2}}
        res = self.i._update_old_match(old_match, child_match, keys, genomic=True)
        assert res == {'key1': [{'one': 1}, {'two': 2}]}, res

    def test_intersect_results_gandg1(self):

        # AND Intersection between genomic nodes with all inclusion criteria
        # ------------------------------------------------------------------------
        # parent: AND
        # child1: GENOMIC
            # (y) DEV-01 variants: BRAF p.V600E mutation & BRAF p.V600D mutation
            # (n) DEV-02 variants: BRAF p.V600E mutation & BRAF p.V600D mutation
            # (y) DEV-03 variants: BRAF p.V600D mutation
        # child2: GENOMIC
            # (y) DEV-01 variants: MET exon 14 In_Frame_Del
            # (y) DEV-03 variants: MET exon 13 In_Frame_Del

        node = {'type': 'and'}
        child1 = {
            'type': 'genomic',
            'matches': [
                {
                    kn.mrn_col: '01', kn.sample_id_col: 'DEV-01',
                    kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600E'},
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'}
                    ]
                },
                {
                    kn.mrn_col: '01', kn.sample_id_col: 'DEV-02',
                    kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600E'},
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'}
                    ]
                },
                {
                    kn.mrn_col: '01', kn.sample_id_col: 'DEV-03',
                    kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'}
                    ]
                }
            ]
        }
        child2 = {
            'type': 'genomic',
            'matches': [
                {
                    kn.mrn_col: '01', kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.sample_id_col: 'DEV-01',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'MET', kn.transcript_exon_col: 14, kn.variant_class_col: 'In_Frame_Del'},
                    ]
                },
                {
                    kn.mrn_col: '01', kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.sample_id_col: 'DEV-03',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'MET', kn.transcript_exon_col: 13, kn.variant_class_col: 'In_Frame_Del'},
                    ]
                }
            ]
        }
        self.i.intersect_results(node=node, children=[child1, child2])
        assert node['matches'] == [
            {
                kn.mrn_col: '01', kn.sample_id_col: 'DEV-01',
                kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                kn.mutation_list_col: [
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600E'},
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'},
                    {kn.transcript_exon_col: 14, kn.hugo_symbol_col: 'MET', kn.variant_class_col: 'In_Frame_Del'}
                ]
            },
            {
                kn.mrn_col: '01', kn.sample_id_col: 'DEV-03',
                kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                kn.mutation_list_col: [
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'},
                    {kn.transcript_exon_col: 13, kn.hugo_symbol_col: 'MET', kn.variant_class_col: 'In_Frame_Del'}
                ]
            }
        ], node['matches']

    def test_intersect_results_gandg2(self):

        # AND Intersection between genomic nodes with inclusion and exclusion criteria
        # ------------------------------------------------------------------------
        # parent: AND
        # child1: GENOMIC
            # (y) DEV-01 variants: BRAF p.V600E mutation & BRAF p.V600D mutation
            # (y) DEV-02 exclusion_reasons: !ERBB2 mutation & !BRAF p.V600E
            # (y) DEV-03 variants: BRAF p.V600D mutation
        # child2: GENOMIC
            # (y) DEV-01 exclusion_reasons: !RET SV
            # (y) DEV-02 exclusion_reasons: !RET SV
            # (y) DEV-03 variants: MET exon 13 In_Frame_Del
            #            exclusion_reasons: !RET SV

        node = {'type': 'and'}
        child1 = {
            'type': 'genomic',
            'matches': [
                {
                    kn.mrn_col: '01', kn.sample_id_col: 'DEV-01',
                    kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600E'},
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'}
                    ]
                },
                {
                    kn.mrn_col: '01', kn.sample_id_col: 'DEV-02',
                    kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    'genomic_exclusion_reasons': [
                        {kn.hugo_symbol_col: 'ERBB2'},
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600E'}
                    ]
                },
                {
                    kn.mrn_col: '01', kn.sample_id_col: 'DEV-03',
                    kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'}
                    ]
                }
            ]
        }
        child2 = {
            'type': 'genomic',
            'matches': [
                {
                    kn.mrn_col: '01', kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.sample_id_col: 'DEV-01',
                    'genomic_exclusion_reasons': [
                        {kn.hugo_symbol_col: 'RET', kn.variant_category_col: s.variant_category_sv_val}
                    ]
                },
                {
                    kn.mrn_col: '01', kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.sample_id_col: 'DEV-02',
                    'genomic_exclusion_reasons': [
                        {kn.hugo_symbol_col: 'RET', kn.variant_category_col: s.variant_category_sv_val}
                    ]
                },
                {
                    kn.mrn_col: '01', kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.sample_id_col: 'DEV-03',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'MET', kn.transcript_exon_col: 13, kn.variant_class_col: 'In_Frame_Del'},
                    ],
                    'genomic_exclusion_reasons': [
                        {kn.hugo_symbol_col: 'RET', kn.variant_category_col: s.variant_category_sv_val}
                    ]
                }
            ]
        }
        self.i.intersect_results(node=node, children=[child1, child2])
        assert node['matches'] == [
            {
                kn.mrn_col: '01', kn.sample_id_col: 'DEV-01',
                kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                kn.mutation_list_col: [
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600E'},
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'},
                ],
                'genomic_exclusion_reasons': [
                    {kn.hugo_symbol_col: 'RET', kn.variant_category_col: s.variant_category_sv_val}
                ]
            },
            {
                kn.mrn_col: '01', kn.sample_id_col: 'DEV-02',
                kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                'genomic_exclusion_reasons': [
                    {kn.hugo_symbol_col: 'ERBB2'},
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600E'},
                    {kn.hugo_symbol_col: 'RET', kn.variant_category_col: s.variant_category_sv_val}
                ]
            },
            {
                kn.mrn_col: '01', kn.sample_id_col: 'DEV-03',
                kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                kn.mutation_list_col: [
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'},
                    {kn.transcript_exon_col: 13, kn.hugo_symbol_col: 'MET', kn.variant_class_col: 'In_Frame_Del'}
                ],
                'genomic_exclusion_reasons': [
                    {kn.hugo_symbol_col: 'RET', kn.variant_category_col: s.variant_category_sv_val}
                ]
            }
        ], self._print(node['matches'])

    def test_intersect_results_gorg1(self):

        # OR Intersection between genomic nodes with all inclusion criteria
        # ------------------------------------------------------------------------
        # parent: OR
        # child1: GENOMIC
            # (y) DEV-01 variants: BRAF p.V600E mutation & BRAF p.V600D mutation
            # (y) DEV-02 variants: BRAF p.V600E mutation & BRAF p.V600D mutation
            # (y) DEV-03 variants: BRAF p.V600D mutation
        # child2: GENOMIC
            # (y) DEV-01 variants: MET exon 14 In_Frame_Del
            # (y) DEV-04 variants: MET exon 13 In_Frame_Del

        node = {'type': 'or'}
        child1 = {
            'type': 'genomic',
            'matches': [
                {
                    kn.mrn_col: '01', kn.sample_id_col: 'DEV-01',
                    kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600E'},
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'}
                    ]
                },
                {
                    kn.mrn_col: '01', kn.sample_id_col: 'DEV-02',
                    kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600E'},
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'}
                    ]
                },
                {
                    kn.mrn_col: '01', kn.sample_id_col: 'DEV-03',
                    kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'}
                    ]
                }
            ]
        }
        child2 = {
            'type': 'genomic',
            'matches': [
                {
                    kn.mrn_col: '01', kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.sample_id_col: 'DEV-01',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'MET', kn.transcript_exon_col: 14, kn.variant_class_col: 'In_Frame_Del'},
                    ]
                },
                {
                    kn.mrn_col: '01', kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.sample_id_col: 'DEV-04',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'MET', kn.transcript_exon_col: 13, kn.variant_class_col: 'In_Frame_Del'},
                    ]
                }
            ]
        }
        self.i.intersect_results(node=node, children=[child1, child2])
        assert node['matches'] == [
            {
                kn.mrn_col: '01', kn.sample_id_col: 'DEV-01',
                kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                kn.mutation_list_col: [
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600E'},
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'}
                ]
            },
            {
                kn.mrn_col: '01', kn.sample_id_col: 'DEV-02',
                kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                kn.mutation_list_col: [
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600E'},
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'},
                ]
            },
            {
                kn.mrn_col: '01', kn.sample_id_col: 'DEV-03',
                kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                kn.mutation_list_col: [
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'},
                ]
            },
            {
                kn.mrn_col: '01', kn.sample_id_col: 'DEV-01',
                kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                kn.mutation_list_col: [
                    {kn.transcript_exon_col: 14, kn.hugo_symbol_col: 'MET', kn.variant_class_col: 'In_Frame_Del'}
                ]
            },
            {
                kn.mrn_col: '01', kn.sample_id_col: 'DEV-04',
                kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                kn.mutation_list_col: [
                    {kn.transcript_exon_col: 13, kn.hugo_symbol_col: 'MET', kn.variant_class_col: 'In_Frame_Del'}
                ]
            }
        ], self._print(node['matches'])

    def test_intersect_results_candg1(self):

        # AND Intersection between clinical and genomic nodes
        # ------------------------------------------------------------------------
        # parent: AND
        # child1: GENOMIC
            # (y) DEV-01 variants: BRAF p.V600E mutation & BRAF p.V600D mutation
            # (n) DEV-02 variants: BRAF p.V600E mutation & BRAF p.V600D mutation
            # (y) DEV-03 variants: BRAF p.V600D mutation
        # child2: CLINICAL
            # (y) DEV-01: Lung Adenocarcinoma & !Melanoma
            # (y) DEV-03: Melanoma

        node = {'type': 'and'}
        child1 = {
            'type': 'genomic',
            'matches': [
                {
                    kn.mrn_col: '01', kn.sample_id_col: 'DEV-01',
                    kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600E'},
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'}
                    ]
                },
                {
                    kn.mrn_col: '01', kn.sample_id_col: 'DEV-02',
                    kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600E'},
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'}
                    ]
                },
                {
                    kn.mrn_col: '01', kn.sample_id_col: 'DEV-03',
                    kn.oncotree_primary_diagnosis_name_col: 'Melanoma',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'}
                    ]
                }
            ]
        }
        child2 = {
            'type': 'clinical',
            'matches': [
                {
                    kn.mrn_col: '01', kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.sample_id_col: 'DEV-01',
                    'clinical_exclusion_reasons': [
                        {kn.oncotree_primary_diagnosis_name_col: 'Melanoma'}
                    ]
                },
                {
                    kn.mrn_col: '01', kn.oncotree_primary_diagnosis_name_col: 'Melanoma',
                    kn.sample_id_col: 'DEV-03',
                }
            ]
        }
        self.i.intersect_results(node=node, children=[child1, child2])
        assert node['matches'] == [
            {
                kn.mrn_col: '01', kn.sample_id_col: 'DEV-01',
                kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                kn.mutation_list_col: [
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600E'},
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'}
                ],
                'clinical_exclusion_reasons': [
                    {kn.oncotree_primary_diagnosis_name_col: 'Melanoma'}
                ]
            },
            {
                kn.mrn_col: '01', kn.sample_id_col: 'DEV-03',
                kn.oncotree_primary_diagnosis_name_col: 'Melanoma',
                kn.mutation_list_col: [
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'}
                ]
            }
        ], self._print(node['matches'])

    def test_intersect_results_aora1(self):

        # OR Intersection between genomic nodes with all inclusion criteria
        # ------------------------------------------------------------------------
        # parent: OR
        # child1: AND
            # (y) DEV-01 variants: BRAF p.V600E mutation & BRAF p.V600D mutation
            # (y) DEV-02 variants: BRAF p.V600E mutation & BRAF p.V600D mutation
            # (y) DEV-03 variants: BRAF p.V600D mutation
        # child2: AND
            # (y) DEV-01 variants: MET exon 14 In_Frame_Del
            # (y) DEV-04 variants: MET exon 13 In_Frame_Del

        node = {'type': 'or'}
        child1 = {
            'type': 'and',
            'matches': [
                {
                    kn.mrn_col: '01', kn.sample_id_col: 'DEV-01',
                    kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600E'},
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'}
                    ]
                },
                {
                    kn.mrn_col: '01', kn.sample_id_col: 'DEV-02',
                    kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600E'},
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'}
                    ]
                },
                {
                    kn.mrn_col: '01', kn.sample_id_col: 'DEV-03',
                    kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'}
                    ]
                }
            ]
        }
        child2 = {
            'type': 'and',
            'matches': [
                {
                    kn.mrn_col: '01', kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.sample_id_col: 'DEV-01',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'MET', kn.transcript_exon_col: 14, kn.variant_class_col: 'In_Frame_Del'},
                    ]
                },
                {
                    kn.mrn_col: '01', kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                    kn.sample_id_col: 'DEV-04',
                    kn.mutation_list_col: [
                        {kn.hugo_symbol_col: 'MET', kn.transcript_exon_col: 13, kn.variant_class_col: 'In_Frame_Del'},
                    ]
                }
            ]
        }
        self.i.intersect_results(node=node, children=[child1, child2])
        assert node['matches'] == [
            {
                kn.mrn_col: '01', kn.sample_id_col: 'DEV-01',
                kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                kn.mutation_list_col: [
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600E'},
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'}
                ]
            },
            {
                kn.mrn_col: '01', kn.sample_id_col: 'DEV-02',
                kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                kn.mutation_list_col: [
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600E'},
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'},
                ]
            },
            {
                kn.mrn_col: '01', kn.sample_id_col: 'DEV-03',
                kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                kn.mutation_list_col: [
                    {kn.hugo_symbol_col: 'BRAF', kn.protein_change_col: 'p.V600D'},
                ]
            },
            {
                kn.mrn_col: '01', kn.sample_id_col: 'DEV-01',
                kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                kn.mutation_list_col: [
                    {kn.transcript_exon_col: 14, kn.hugo_symbol_col: 'MET', kn.variant_class_col: 'In_Frame_Del'}
                ]
            },
            {
                kn.mrn_col: '01', kn.sample_id_col: 'DEV-04',
                kn.oncotree_primary_diagnosis_name_col: 'Lung Adenocarcinoma',
                kn.mutation_list_col: [
                    {kn.transcript_exon_col: 13, kn.hugo_symbol_col: 'MET', kn.variant_class_col: 'In_Frame_Del'}
                ]
            }
        ], self._print(node['matches'])


