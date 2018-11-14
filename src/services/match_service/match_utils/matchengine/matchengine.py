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
        self.proj_dict = {True: 'inclusion_reasons', False: 'exclusion_reasons'}

        self.matched_results = []
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

    def traverse_match_tree(self):
        """
        Construct a MongoDB query that represents the match tree

        :return: {dict}
        """
        # todo unit test
        for node_id in list(nx.dfs_postorder_nodes(self.match_tree_nx, source=1)):

            # access node and its children
            node = self.match_tree_nx.node[node_id]
            children = [self.match_tree_nx.node[n] for n in self.match_tree_nx.successors(node_id)]

            # clinical nodes
            if node['type'] == 'clinical':
                node = self._assess_clinical_node(node=node)
                node['matched_results'] = self._search_for_matching_records(node=node)

            # genomic nodes
            elif node['type'] == 'genomic':
                node = self._assess_genomic_node(node=node)
                node['matched_results'] = self._search_for_matching_records(node=node)

            # join child queries with "and"
            elif node['type'] == 'and' or node['type'] == 'or':
                node = self._intersect_results(node=node, children=children)

            else:
                raise ValueError('match tree node must be of type "clinical", "genomic", "and", or "or')

        self.matched_results = node['matched_results']

    def _assess_clinical_node(self, node):
        """
        Assess the given node and construct the appropriate MongoDB query.

        :param node: {digraph node}
        :return: {tuple} (MongoDB query, projection, {bool}}
        """
        query = {'$and': []}
        proj_info = []
        criteria = sorted(node['value'].keys())

        if s.mt_diagnosis not in node['value']:
            raise ValueError('%s column must be included for all clinical nodes' % s.mt_diagnosis)

        # diagnosis query
        include = True
        if s.mt_diagnosis in criteria:

            cancer_type = node['value'][s.mt_diagnosis]
            include = me_utils.assess_inclusion(cancer_type)
            subquery = self.create_oncotree_diagnosis_query(cancer_type=me_utils.sanitize_exclusion_vals(cancer_type),
                                                            include=include)
            query['$and'].append(subquery)
            proj_info.append({s.mt_diagnosis: cancer_type})

        # age query
        if s.mt_age in criteria:
            age = node['value'][s.mt_age]
            subquery = self.create_age_query(age=age)
            query['$and'].append(subquery)
            proj_info.append({s.mt_age: age})

        # gender query
        if s.mt_gender in criteria:
            gender = node['value'][s.mt_gender]
            subquery = self.create_gender_query(gender=gender)
            query['$and'].append(subquery)
            proj_info.append({s.mt_gender: gender})

        # clinical projection
        proj_keys = [i.keys()[0] for i in proj_info]
        proj_vals = [i.values()[0] for i in proj_info]
        node['clinical_%s' % self.proj_dict[include]] = self.create_clinical_proj(include=include,
                                                                                  keys=proj_keys,
                                                                                  vals=proj_vals)

        node['query'] = query

    def _assess_genomic_node(self, node):
        """
        Assess the given node and construct the appropriate MongoDB query.

        :param node: {digraph node}
        :return: {dict}
        """
        criteria = sorted(node['value'].keys())

        vc = None
        include = True
        variant_category = None
        if s.mt_variant_category in node['value']:
            variant_category = me_utils.sanitize_exclusion_vals(node['value'][s.mt_variant_category])
            variant_category = me_utils.normalize_variant_category_val(variant_category)
            include = me_utils.assess_inclusion(node_value=node['value'][s.mt_variant_category])
            vc = self.variant_category_dict[variant_category]

        # gene level query
        if criteria == [s.mt_hugo_symbol, s.mt_variant_category]:
            node['variant_level'] = 'gene'
            gene_name = node['value'][s.mt_hugo_symbol]

            # Structural Variants
            if variant_category == s.variant_category_sv_val:
                node['query'] = self.create_sv_query(gene_name=gene_name, include=include)
                node['genomic_%s' % self.proj_dict[include]] = \
                    self.create_genomic_proj(include=include,
                                             query=node['query'],
                                             keys=[vc, self.hugo_symbol_key],
                                             vals=[variant_category, gene_name])
                return node

            # Mutations and CNVs
            else:
                node['query'] = self.create_gene_level_query(gene_name=gene_name,
                                                             variant_category=variant_category,
                                                             include=include)

                node['genomic_%s' % self.proj_dict[include]] = \
                    self.create_genomic_proj(include=include,
                                             query=node['query'],
                                             keys=[vc, self.hugo_symbol_key],
                                             vals=[variant_category, gene_name])
                return node

        # variant-level mutation criteria
        elif s.mt_protein_change in criteria:
            node['variant_level'] = 'variant'
            gene_name = node['value'][s.mt_hugo_symbol]
            protein_change = node['value'][s.mt_protein_change]

            node['query'] = self.create_mutation_query(gene_name=gene_name,
                                                       protein_change=protein_change,
                                                       include=include)

            node['genomic_%s' % self.proj_dict[include]] = \
                self.create_genomic_proj(include=include,
                                         query=node['query'],
                                         keys=[vc, self.hugo_symbol_key, self.protein_change_key],
                                         vals=[variant_category, gene_name, protein_change])
            return node

        # wildcard-level mutation criteria
        elif s.mt_wc_protein_change in criteria:
            node['variant_level'] = 'wildcard'
            gene_name = node['value'][s.mt_hugo_symbol]
            protein_change = node['value'][s.mt_wc_protein_change]

            node['query'] = self.create_wildcard_query(gene_name=gene_name,
                                                       protein_change=protein_change,
                                                       include=include)

            node['genomic_%s' % self.proj_dict[include]] = \
                self.create_genomic_proj(include=include,
                                         query=node['query'],
                                         keys=[vc, self.hugo_symbol_key, self.ref_residue_key],
                                         vals=[variant_category, gene_name, protein_change])
            return node

        # exon-level mutation criteria
        elif s.mt_exon in criteria:
            node['variant_level'] = 'exon'
            gene_name = node['value'][s.mt_hugo_symbol]
            exon = node['value'][s.mt_exon]
            variant_class = node['value'][s.mt_variant_class] if s.mt_variant_class in node['value'] else None

            node['query'] = self.create_exon_query(gene_name=gene_name,
                                                   exon=exon,
                                                   variant_class=variant_class,
                                                   include=include)

            node['genomic_%s' % self.proj_dict[include]] = \
                self.create_genomic_proj(include=include,
                                         query=node['query'],
                                         keys=[vc, self.hugo_symbol_key, self.transcript_exon_key, self.variant_class_key],
                                         vals=[variant_category, gene_name, exon, variant_class])
            return node

        # cnv criteria
        elif s.mt_cnv_call in criteria:
            gene_name = node['value'][s.mt_hugo_symbol]
            cnv_call = node['value'][s.mt_cnv_call]

            node['query'] = self.create_cnv_query(gene_name=gene_name,
                                                  cnv_call=cnv_call,
                                                  include=include)

            node['genomic_%s' % self.proj_dict[include]] =\
                self.create_genomic_proj(include=include,
                                         query=node['query'],
                                         keys=[vc, self.hugo_symbol_key, self.cnv_call_key],
                                         vals=[variant_category, gene_name, cnv_call])
            return node

        # mutational signature criteria
        elif any([criterion in s.mt_signature_cols for criterion in criteria]):
            for sig in s.mt_signature_cols:
                sigtype, sigval = me_utils.normalize_signature_vals(signature_type=sig, signature_val=node['value'][sig])
                node['query'] = self.create_mutational_signature_query(signature_type=sigtype, signature_val=sigval)
                node['genomic_inclusion_reasons'] = self.create_genomic_proj(include=True, query=node['query'])
                return node

        # wildtype criteria
        elif s.mt_wildtype in node['value'] and node['value'][s.mt_wildtype] is True:
            gene_name = node['value'][s.mt_hugo_symbol]
            node['query'] = self.create_gene_level_query(gene_name=gene_name,
                                                         variant_category=s.variant_category_wt_val,
                                                         include=True)

            node['genomic_inclusion_reasons'] = self.create_genomic_proj(include=True, query=node['query'])
            return node

        # low-coverage criteria
        # todo build out low coverage criteria logic
        else:
            raise ValueError('This node does not match an expected format.')

    def _intersect_results(self, node, children):
        """
        Intersect match results by sample Id.

        :param node: {digraph node}
        :return: {digraph node}
        """

        # todo this needs to be tested thorougly
        intersection_dict = {'and': set.intersection_update, 'or': set.update}
        matched_sample_ids = set(i[kn.sample_id_col] for i in children[0]['matched_results'])
        node['matched_results'] = children[0]['matched_results'][:]

        for child in children:
            child_matched_sample_ids = set(i[kn.sample_id_col] for i in child['matched_results'])
            intersection_dict[node['type']](matched_sample_ids, child_matched_sample_ids)

            # todo can this be done with groupby?
            # keep existing matches
            node['matched_results'] = [i for i in node['matched_results'] if i[kn.sample_id_col] in matched_sample_ids]
            old_sample_ids = [i[kn.sample_id_col] for i in node['matched_results']]

            # add new matches, appending novel reasons as they come
            for child_match in child['matched_results'][:]:
                if child_match[kn.sample_id_col] in matched_sample_ids:

                    # update existing matches
                    if child_match[kn.sample_id_col] in old_sample_ids:
                        old_match = [i for i in node['matched_results']
                                     if i[kn.sample_id_col] == child_match[kn.sample_id_col]][0]
                        all_keys = ['genomic_exclusion_reasons', 'clinical_exclusion_reasons',
                                    kn.mutation_list_col, kn.cnv_list_col, kn.sv_list_col, kn.wt_genes_col]

                        # todo add signatures
                        for key in all_keys:
                            if key in child_match:
                                cm = child_match[key].copy()
                                if isinstance(old_match[key], dict):
                                    om = []

                                om.append(cm)
                                old_match[key] = om

                    # add new matches
                    else:
                        node['matched_results'].extend([i for i in child['matched_results']
                                                        if i[kn.sample_id_col] in matched_sample_ids])

        return node

    def _search_for_matching_records(self, node):
        """
        Search for any sample records that match the constructed query

        :param node: {digraph node}
        :return: {null}
        """

        # include inclusion reasons in projection
        if 'genomic_inclusion_reasons' in node:
            proj = node['genomic_inclusion_reasons']
        elif 'clinical_inclusion_reasons' in node:
            proj = node['clinical_inclusion_reasons']
        else:
            proj = self.proj.copy()

        # perform query
        matches = list(self.db[s.sample_collection_name].find(node['query'], proj))

        # add exclusion reasons to match results
        for match in matches:
            if kn.mutation_list_col in match:
                for variant in match[kn.mutation_list_col]:
                    variant[kn.mr_inclusion_criteria_col] = 'genomic_inclusion_reasons' in node
                    if 'variant_level' in node:
                        variant[kn.mr_reason_level_col] = node['variant_level']

            elif 'genomic_exclusion_reasons' in node:
                match['genomic_exclusion_reasons'] = node['genomic_exclusion_reasons']
            elif 'clinical_exclusion_reasons' in node:
                match['clinical_exclusion_reasons'] = node['clinical_exclusion_reasons']

        return matches

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
