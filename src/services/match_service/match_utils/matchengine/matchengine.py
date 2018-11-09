import logging
import networkx as nx

from src.utilities import settings as s
from src.utilities.utilities import get_db
from src.data_store import key_names as kn
from src.services.match_service.match_utils.sort import add_sort_order
from src.services.match_service.match_utils.matchengine import matchengine_utils as me_utils
from src.services.match_service.query_utils.clinical_queries import ClinicalQueries
from src.services.match_service.query_utils.genomic_queries import GenomicQueries
from src.services.match_service.query_utils.proj_utils import ProjUtils

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s', )


class MatchEngine(ClinicalQueries, GenomicQueries, ProjUtils):

    def __init__(self, match_tree, trial_info):
        ClinicalQueries.__init__(self)
        GenomicQueries.__init__(self)
        ProjUtils.__init__(self)

        self.trial_info = trial_info
        self.match_tree = match_tree
        self.match_tree_nx = None
        self.db = get_db()
        self.query = {}

        self.matched_samples = []
        self.trial_matches = None

    def convert_match_tree_to_digraph(self):
        """
        Converts a match tree in JSON format into a networkx directed graph
        Given json object of MATCH clause, the function returns a directed graph

        :return: {diGraph object}
        """
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

            # access node and its children
            node = self.match_tree_nx.node[node_id]
            children = [self.match_tree_nx.node[n] for n in self.match_tree_nx.successors(node_id)]
            parent = self.match_tree_nx.successsors(self.match_tree_nx.predecessors(node_id)[0])
            siblings = [self.match_tree_nx.node[n] for n in parent if n != node_id]

            # clinical nodes
            if node['type'] == 'clinical':
                node['query'] = self._assess_clinical_node(node=node)

            # genomic nodes
            elif node['type'] == 'genomic':
                node['query'] = self._assess_genomic_node(node=node)

            # join child queries with "and"
            elif node['type'] == 'and':
                node['query'] = {'$and': []}
                for child in children:
                    node['query']['$and'].append(child['query'])

            elif node['type'] == 'or':
                node['query'] = {'$or': []}
                for child in children:
                    node['query']['$or'].append(child['query'])

            else:
                raise ValueError('match tree node must be of type "clinical", "genomic", "and", or "or')

        self.query = self.match_tree_nx.node[1]['query']

    def _assess_clinical_node(self, node, siblings):
        """
        Assess the given node and construct the appropriate MongoDB query.

        :param node: {digraph node}
        :param siblings: {list of dict}
        :return: {dict}
        """
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
            age = node['value'][s.mt_age]
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

        # wildtype criteria
        # todo build out wildtype criteria logic

        # low-coverage criteria
        # todo build out low coverage criteria logic

    def search_for_matching_records(self):
        """
        Search for any sample records that match the constructed query

        :return: {null}
        """
        self.matched_samples = list(self.db[s.sample_collection_name].find(self.query, self.proj))
        logging.info('%d samples matched' % len(self.matched_samples))

    def create_trial_match_records(self):
        """
        Create trial match records from matched samples,
        including clinical and genomic reasons for each match

        :return: {null}
        """
        for sample in self.matched_samples:

            trial_match_doc = {
                kn.tm_sample_id_col: sample[kn.sample_id_col],
                kn.tm_trial_protocol_no_col: self.trial_info['protocol_no'],
                kn.tm_mrn_col: sample[kn.mrn_col],
                kn.tm_vital_status_col: sample[kn.vital_status_col],
                kn.tm_trial_accrual_status_col: self.trial_info['accrual_status'],
                kn.tm_sort_order_col: 0,
                kn.tm_match_reasons_col: []
            }


    def sort_trial_matches(self):
        """
        Sort trial matches.

        :return: {Pandas dataframe}
        """
        # todo unit test
        if self.trial_matches is None:
            return

        logging.info('Sorting trial matches')
        return add_sort_order(self.trial_matches)
