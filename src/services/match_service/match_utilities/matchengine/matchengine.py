import networkx as nx

from src.utilities import settings as s
from src.data_store import key_names as kn
from src.services.match_service.match_utilities.matchengine import matchengine_utilities as me_utils
from src.services.match_service.query_utilities.clinical_queries import ClinicalQueries
from src.services.match_service.query_utilities.genomic_queries import GenomicQueries


# todo move to two files: Core Matchengine and Matchengine Utils ??
class MatchEngine(ClinicalQueries, GenomicQueries):

    def __init__(self, match_tree, trial_level):
        ClinicalQueries.__init__(self)
        GenomicQueries.__init__(self)

        self.match_tree = match_tree
        self.trial_level = trial_level
        self.match_tree_nx = None
        self.query = {}

    def convert_match_tree_to_digraph(self):
        """
        Converts a match tree in JSON format into a networkx directed graph
        Given json object of MATCH clause, the function returns a directed graph

        :return: {diGraph object}
        """
        # todo unit test
        key = self.match_tree.keys()[0]
        value = self.match_tree[key]
        global_node = 1
        self.match_tree_nx = nx.DiGraph()
        s = []
        s.append([0, global_node, key, value])
        while len(s) > 0:
            current = s.pop(0)
            parent = current[0]
            node = current[1]
            key = current[2]
            value = current[3]
            self.match_tree_nx.add_node(node)
            self.match_tree_nx.add_edges_from([(parent, node)])
            self.match_tree_nx.node[node]['type'] = key
            if isinstance(value, dict):
                self.match_tree_nx.node[node]['value'] = value
            elif isinstance(value, list):
                for i in range(0, len(value)):
                    global_node += 1
                    s.append([node, global_node, value[i].keys()[0], value[i][value[i].keys()[0]]])

        self.match_tree_nx.remove_node(0)

    def create_mongo_query_from_match_tree(self):
        """
        Construct a MongoDB query that represents the match tree

        :return: {dict}
        """
        # todo unit test
        for node_id in list(nx.dfs_postorder_nodes(self.match_tree_nx, source=1)):
            node = self.match_tree_nx.node[node_id]
            if node['type'] == 'clinical':
                subquery = self._assess_genomic_node(node=node)
            elif node['type'] == 'genomic':
                subquery = self._assess_genomic_node(node=node)
            elif node['type'] == 'and':
                # todo add and node logic
                pass
            elif node['type'] == 'or':
                # todo add or node logic
                pass
            else:
                raise ValueError('match tree node must be of type "clinical", "genomic", "and", or "or')

    def _assess_clinical_node(self, node):
        """
        Assess the given node and construct the appropriate MongoDB query.

        :param node: {digraph node}
        :return: {dict}
        """
        # todo unit test
        query = {'$and': []}
        criteria = sorted(node['value'].keys())

        if s.mt_diagnosis not in node['value']:
            raise ValueError('%s column must be included for all clinical nodes' % s.mt_diagnosis)

        # diagnosis query
        if s.mt_diagnosis in criteria:
            cancer_type = node['value'][s.mt_diagnosis]
            include = me_utils.assess_inclusion(cancer_type)
            subquery = self.create_oncotree_diagnosis_query(cancer_type=me_utils.sanitize_exclusion_vals(cancer_type),
                                                            include=include)
            query['$and'].append(subquery)

        # age query
        if s.mt_age in criteria:
            age = node['value'][s.mt_diagnosis]
            subquery = self.create_age_query(age=age)
            query['$and'].append(subquery)

        # gender query
        if s.mt_gender in criteria:
            gender = node['value'][s.mt_gender]
            subquery = self.create_gender_query(gender=gender)
            query['$and'].append(subquery)

        return query

    def _assess_genomic_node(self, node):
        """
        Assess the given node and construct the appropriate MongoDB query.

        :param node: {digraph node}
        :return: {dict}
        """
        # todo unit test
        criteria = sorted(node['value'].keys())

        # gene level query
        if criteria == [s.mt_hugo_symbol, s.mt_variant_category]:
            gene_name = node['value'][s.mt_hugo_symbol]
            variant_category = me_utils.normalize_variant_category_val(node['value'][s.mt_variant_category])
            include = me_utils.assess_inclusion(node_value=variant_category)

            # Structural Variants
            if variant_category == s.variant_category_sv_val:
                return self.create_sv_query(gene_name=gene_name, include=include)

            # Mutations and CNVs
            else:
                return self.create_gene_level_query(gene_name=gene_name,
                                                    variant_category=me_utils.sanitize_exclusion_vals(variant_category),
                                                    include=include)
        # variant-level mutation criteria
        elif s.mt_protein_change in criteria:
            gene_name = node['value'][s.mt_hugo_symbol]
            protein_change = node['value'][s.mt_protein_change]
            variant_category = me_utils.normalize_variant_category_val(node['value'][s.mt_variant_category])
            include = me_utils.assess_inclusion(node_value=variant_category)
            return self.create_mutation_query(gene_name=gene_name,
                                              protein_change=protein_change,
                                              include=include)
        # wildcard-level mutation criteria
        elif s.mt_wc_protein_change in criteria:
            gene_name = node['value'][s.mt_hugo_symbol]
            protein_change = node['value'][s.mt_wc_protein_change]
            variant_category = me_utils.normalize_variant_category_val(node['value'][s.mt_variant_category])
            include = me_utils.assess_inclusion(node_value=variant_category)
            return self.create_wildcard_query(gene_name=gene_name,
                                              protein_change=protein_change,
                                              include=include)
        # exon-level mutation criteria
        elif s.mt_exon in criteria:
            gene_name = node['value'][s.mt_hugo_symbol]
            exon = node['value'][s.mt_exon]
            variant_category = me_utils.normalize_variant_category_val(node['value'][s.mt_variant_category])
            include = me_utils.assess_inclusion(node_value=variant_category)
            return self.create_exon_query(gene_name=gene_name,
                                          exon=exon,
                                          include=include)
        # cnv criteria
        elif s.mt_cnv_call in criteria:
            gene_name = node['value'][s.mt_hugo_symbol]
            cnv_call = node['value'][s.mt_cnv_call]
            variant_category = me_utils.normalize_variant_category_val(node['value'][s.mt_variant_category])
            include = me_utils.assess_inclusion(node_value=variant_category)
            return self.create_cnv_query(gene_name=gene_name,
                                         cnv_call=cnv_call,
                                         include=include)

        # mutational signature criteria
        elif any([criterion in s.mt_signature_cols for criterion in criteria]):
            for sig in s.mt_signature_cols:
                sigtype, sigval = me_utils.normalize_signature_vals(signature_type=sig, signature_val=node['value'][sig])
                return self.create_mutational_signature_query(signature_type=sigtype, signature_val=sigval)
                # todo add TMZ, Tobacco, etc. statuses

        # low-coverage criteria
        # todo build out low coverage criteria logic

    def search_for_matching_records(self):
        # todo unit test
        raise NotImplementedError
