from src.utilities import settings as s
from src.data_store import key_names as kn
from tests.test_match_service import TestQueryUtilitiesShared
from src.services.match_service.match_utils.matchengine.assess_node_utils import AssessNodeUtils


class TestAssessNodeUtils(TestQueryUtilitiesShared):

    def setUp(self):
        super(TestAssessNodeUtils, self).setUp()
        self.a = AssessNodeUtils()
        self.query = {'$and': []}
        self.proj_info = []

    def tearDown(self):
        pass

    def test_parse_diagnosis(self):

        # inclusion
        node = {'value': {s.mt_diagnosis: 'Lung Adenocarcinoma'}}
        self.a._parse_diagnosis(node=node, query=self.query, proj_info=self.proj_info)
        assert self.query['$and'][0] == {kn.oncotree_primary_diagnosis_name_col: {'$in': ['Lung Adenocarcinoma']}}
        assert self.proj_info[0] == {s.mt_diagnosis: 'Lung Adenocarcinoma'}

        # exclusion
        node = {'value': {s.mt_diagnosis: '!Lung Adenocarcinoma'}}
        self.a._parse_diagnosis(node=node, query=self.query, proj_info=self.proj_info)
        assert self.query['$and'][1] == {kn.oncotree_primary_diagnosis_name_col: {'$nin': ['Lung Adenocarcinoma']}}
        assert self.proj_info[1] == {s.mt_diagnosis: '!Lung Adenocarcinoma'}

    def test_parse_age(self):

        node = {'value': {s.mt_age: '>=18'}}
        self.a._parse_age(node=node, query=self.query, proj_info=self.proj_info)
        assert self.query['$and'][0].keys() == [kn.birth_date_col]
        assert self.query['$and'][0][kn.birth_date_col].keys() == ['$lte']
        assert self.proj_info[0] == {s.mt_age: '>=18'}

    def test_parse_gender(self):

        node = {'value': {s.mt_gender: 'Female'}}
        self.a._parse_gender(node=node, query=self.query, proj_info=self.proj_info)
        assert self.query == {'$and': [{kn.gender_col: 'Female'}]}
        assert self.proj_info == [{s.mt_gender: 'Female'}]

    def test_parse_variant_category(self):

        # inclusive mutation
        node = {'value': {s.mt_variant_category: s.mt_mut_val}}
        vc, i = self.a._parse_variant_category(node=node)
        assert vc == s.variant_category_mutation_val
        assert i is True

        # exclusive mutation
        node = {'value': {s.mt_variant_category: '!%s' % s.mt_mut_val}}
        vc, i = self.a._parse_variant_category(node=node)
        assert vc == s.variant_category_mutation_val
        assert i is False

        # inclusive cnv
        node = {'value': {s.mt_variant_category: s.mt_cnv_val}}
        vc, i = self.a._parse_variant_category(node=node)
        assert vc == s.variant_category_cnv_val
        assert i is True

        # exclusive cnv
        node = {'value': {s.mt_variant_category: '!%s' % s.mt_cnv_val}}
        vc, i = self.a._parse_variant_category(node=node)
        assert vc == s.variant_category_cnv_val
        assert i is False

        # inclusive sv
        node = {'value': {s.mt_variant_category: s.mt_sv_val}}
        vc, i = self.a._parse_variant_category(node=node)
        assert vc == s.variant_category_sv_val
        assert i is True

        # exclusive sv
        node = {'value': {s.mt_variant_category: '!%s' % s.mt_sv_val}}
        vc, i = self.a._parse_variant_category(node=node)
        assert vc == s.variant_category_sv_val
        assert i is False

    def test_parse_gene_level(self):

        # inclusive mutation
        node = {'value': {
            s.mt_variant_category: s.mt_mut_val,
            s.mt_hugo_symbol: 'BRAF'}
        }
        self.a._parse_gene_level(node=node)
        assert 'query' in node
        assert 'genomic_inclusion_reasons' in node
        assert node['genomic_inclusion_reasons'][kn.mutation_list_col] == node['query'][kn.mutation_list_col]
        assert node['variant_level'] == 'gene'

        # exclusive mutation
        node = {'value': {
            s.mt_variant_category: '!%s' % s.mt_mut_val,
            s.mt_hugo_symbol: 'BRAF'}
        }
        self.a._parse_gene_level(node=node)
        assert 'query' in node
        assert 'genomic_exclusion_reasons' in node
        assert node['genomic_exclusion_reasons'] == {
            kn.variant_category_col: s.variant_category_mutation_val,
            kn.hugo_symbol_col: 'BRAF'
        }
        assert node['variant_level'] == 'gene'

        # exclusive cnv
        node = {'value': {
            s.mt_variant_category: s.mt_cnv_val,
            s.mt_hugo_symbol: 'BRAF'}
        }
        self.a._parse_gene_level(node=node)
        assert 'query' in node
        assert 'genomic_inclusion_reasons' in node
        assert node['genomic_inclusion_reasons'][kn.cnv_list_col] == node['query'][kn.cnv_list_col]
        assert node['variant_level'] == 'gene'

        # exclusive cnv
        node = {'value': {
            s.mt_variant_category: '!%s' % s.mt_cnv_val,
            s.mt_hugo_symbol: 'BRAF'}
        }
        self.a._parse_gene_level(node=node)
        assert 'query' in node
        assert 'genomic_exclusion_reasons' in node
        assert node['genomic_exclusion_reasons'] == {
            kn.variant_category_col: s.variant_category_cnv_val,
            kn.hugo_symbol_col: 'BRAF'
        }, node['genomic_exclusion_reasons']
        assert node['variant_level'] == 'gene'

        # inclusive sv
        node = {'value': {
            s.mt_variant_category: s.mt_sv_val,
            s.mt_hugo_symbol: 'BRAF'}
        }
        self.a._parse_gene_level(node=node)
        assert 'query' in node
        assert 'genomic_inclusion_reasons' in node
        assert node['genomic_inclusion_reasons'][kn.sv_list_col] == node['query'][kn.sv_list_col]
        assert node['variant_level'] == 'gene'

        # exclusive sv
        node = {'value': {
            s.mt_variant_category: '!%s' % s.mt_sv_val,
            s.mt_hugo_symbol: 'BRAF'}
        }
        self.a._parse_gene_level(node=node)
        assert 'query' in node
        assert 'genomic_exclusion_reasons' in node
        assert node['genomic_exclusion_reasons'] == {
            kn.variant_category_col: s.variant_category_sv_val,
            kn.hugo_symbol_col: 'BRAF'
        }
        assert node['variant_level'] == 'gene'

    def test_parse_sv(self):

        # inclusive sv
        node = {'value': {
            s.mt_variant_category: s.mt_sv_val,
            s.mt_hugo_symbol: 'BRAF'}
        }
        self.a._parse_gene_level(node=node)
        assert 'query' in node
        assert 'genomic_inclusion_reasons' in node
        assert node['genomic_inclusion_reasons'][kn.sv_list_col] == node['query'][kn.sv_list_col]
        assert node['variant_level'] == 'gene'

        # exclusive sv
        node = {'value': {
            s.mt_variant_category: '!%s' % s.mt_sv_val,
            s.mt_hugo_symbol: 'BRAF'}
        }
        self.a._parse_gene_level(node=node)
        assert 'query' in node
        assert 'genomic_exclusion_reasons' in node
        assert node['genomic_exclusion_reasons'] == {
            kn.variant_category_col: s.variant_category_sv_val,
            kn.hugo_symbol_col: 'BRAF'
        }
        assert node['variant_level'] == 'gene'

    def test_parse_variant_level(self):

        # inclusive
        node = {'value': {
            s.mt_variant_category: s.mt_mut_val,
            s.mt_hugo_symbol: 'BRAF',
            s.mt_protein_change: 'p.V600E'}
        }
        self.a._parse_variant_level(node=node)
        assert 'query' in node
        assert 'genomic_inclusion_reasons' in node
        assert node['genomic_inclusion_reasons'][kn.mutation_list_col] == node['query'][kn.mutation_list_col]
        assert node['variant_level'] == 'variant'

        # exclusive sv
        node = {'value': {
            s.mt_variant_category: '!%s' % s.mt_mut_val,
            s.mt_hugo_symbol: 'BRAF',
            s.mt_protein_change: 'p.V600E'}
        }
        self.a._parse_variant_level(node=node)
        assert 'query' in node
        assert 'genomic_exclusion_reasons' in node
        assert node['genomic_exclusion_reasons'] == {
            kn.variant_category_col: s.variant_category_mutation_val,
            kn.hugo_symbol_col: 'BRAF',
            kn.protein_change_col: 'p.V600E'
        }, node['genomic_exclusion_reasons']
        assert node['variant_level'] == 'variant'

    def test_parse_wildcard_level(self):

        # inclusive
        node = {'value': {
            s.mt_variant_category: s.mt_mut_val,
            s.mt_hugo_symbol: 'BRAF',
            s.mt_wc_protein_change: 'p.V600'}
        }
        self.a._parse_wildcard_level(node=node)
        assert 'query' in node
        assert 'genomic_inclusion_reasons' in node
        assert node['genomic_inclusion_reasons'][kn.mutation_list_col] == node['query'][kn.mutation_list_col]
        assert node['variant_level'] == 'wildcard'

        # exclusive sv
        node = {'value': {
            s.mt_variant_category: '!%s' % s.mt_mut_val,
            s.mt_hugo_symbol: 'BRAF',
            s.mt_wc_protein_change: 'p.V600'}
        }
        self.a._parse_wildcard_level(node=node)
        assert 'query' in node
        assert 'genomic_exclusion_reasons' in node
        assert node['genomic_exclusion_reasons'] == {
            kn.variant_category_col: s.variant_category_mutation_val,
            kn.hugo_symbol_col: 'BRAF',
            kn.ref_residue_col: 'p.V600'
        }, node['genomic_exclusion_reasons']
        assert node['variant_level'] == 'wildcard'

    def test_parse_exon_level(self):

        # inclusive
        node = {'value': {
            s.mt_variant_category: s.mt_mut_val,
            s.mt_hugo_symbol: 'BRAF',
            s.mt_exon: 20}
        }
        self.a._parse_exon_level(node=node)
        assert 'query' in node
        assert 'genomic_inclusion_reasons' in node
        assert node['genomic_inclusion_reasons'][kn.mutation_list_col] == node['query'][kn.mutation_list_col]
        assert node['variant_level'] == 'exon'

        # exclusive sv
        node = {'value': {
            s.mt_variant_category: '!%s' % s.mt_mut_val,
            s.mt_hugo_symbol: 'BRAF',
            s.mt_exon: 20}
        }
        self.a._parse_exon_level(node=node)
        assert 'query' in node
        assert 'genomic_exclusion_reasons' in node
        assert node['genomic_exclusion_reasons'] == {
            kn.variant_category_col: s.variant_category_mutation_val,
            kn.hugo_symbol_col: 'BRAF',
            kn.transcript_exon_col: 20
        }, node['genomic_exclusion_reasons']
        assert node['variant_level'] == 'exon'

    def test_parse_cnv_call(self):
        pass

    def test_parse_signature(self):
        pass

    def test_parse_wildtype(self):
        pass