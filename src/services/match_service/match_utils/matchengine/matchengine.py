import logging
import networkx as nx

from src.utilities import settings as s
from src.utilities.utilities import get_db
from src.data_store import key_names as kn
from src.services.match_service.match_utils.sort import add_sort_order
from src.services.match_service.match_utils.matchengine import matchengine_utils as me_utils
from src.services.match_service.match_utils.matchengine.assess_node_utils import AssessNodeUtils

logging.basicConfig(level=logging.INFO, format='[%(levelname)s] %(message)s', )


class MatchEngine(AssessNodeUtils):

    def __init__(self, match_tree, trial_info):
        AssessNodeUtils.__init__(self)

        self.trial_info = trial_info
        self.match_tree = match_tree
        self.match_tree_nx = None
        self.db = get_db()

        self.matched_results = None
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

        :return: {null}
        """
        # todo unit test
        for node_id in list(nx.dfs_postorder_nodes(self.match_tree_nx, source=1)):

            # access node and its children
            node = self.match_tree_nx.node[node_id]
            children = [self.match_tree_nx.node[n] for n in self.match_tree_nx.successors(node_id)]

            # clinical nodes
            if node['type'] == 'clinical':
                node = self.assess_clinical_node(node=node)
                node['matched_results'] = self._search_for_matching_records(node=node)

            # genomic nodes
            elif node['type'] == 'genomic':
                node = self.assess_genomic_node(node=node)
                print node
                node['matched_results'] = self._search_for_matching_records(node=node)

            # join child queries with "and"
            elif node['type'] == 'and' or node['type'] == 'or':
                self._intersect_results(node=node, children=children)

            else:
                raise ValueError('match tree node must be of type "clinical", "genomic", "and", or "or')

        self.matched_results = self.match_tree_nx.node[1]['matched_results']

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

    @staticmethod
    def _intersect_results(node, children):
        """
        Intersect match results by sample Id.

        :param node: {digraph node}
        :return: {digraph node}
        """

        print '----debug----'
        print 'NODE', node

        # todo this needs to be tested thoroughly
        intersection_dict = {'and': set.intersection_update, 'or': set.update}
        matched_sample_ids = set(i[kn.sample_id_col] for i in children[0]['matched_results'])
        print 'INITIAL MATCHED SAMPLE IDS', matched_sample_ids
        node['matched_results'] = children[0]['matched_results'][:]
        print 'INITIAL MATCHED RESULTS', node['matched_results']

        idx = 1

        for child in children[1:]:
            child_matched_sample_ids = set(i[kn.sample_id_col] for i in child['matched_results'])
            print 'CHILD %d MATCHED RESULTS' % idx, child['matched_results']
            intersection_dict[node['type']](matched_sample_ids, child_matched_sample_ids)

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

                        # preserve clinical and signature information
                        clinical_keys = [kn.oncotree_primary_diagnosis_name_col, kn.birth_date_col, kn.gender_col]
                        for key in clinical_keys + s.signature_cols:
                            if key in child_match and key not in old_match:
                                old_match[key] = child_match[key]

                        # update genomic information
                        genomic_keys = ['genomic_exclusion_reasons', 'clinical_exclusion_reasons',
                                        kn.mutation_list_col, kn.cnv_list_col, kn.sv_list_col, kn.wt_genes_col]
                        for key in genomic_keys:

                            # add new reasons
                            if key in child_match and key not in old_match:
                                old_match[key] = [child_match[key].copy()]
                            elif key in child_match and key in old_match:
                                if isinstance(old_match[key], dict):
                                    old_match[key] = [old_match[key].copy()]

                                old_match[key].append(child_match[key].copy())

                    # add new matches
                    else:
                        node['matched_results'].extend([i for i in child['matched_results']
                                                        if i[kn.sample_id_col] in matched_sample_ids])

            idx += 1

        print 'FINAL MATCHED RESULTS', node['matched_results']
        return node

    def create_trial_match_records(self):
        """
        Create trial match records from matched samples,
        including clinical and genomic reasons for each match

        :return: {null}
        """
        # todo unit test
        trial_match_docs = []
        for sample in self.match_tree_nx.node[1]['matched_results']:

            mut_reasons = []
            cnv_reasons = []
            sv_reasons = []
            wt_reasons = []
            # todo parse matched results
            # todo add signatures
            # todo add low coverage

            match_reasons = {
                kn.mr_trial_level_col: self.trial_info['level'],
                kn.mr_trial_step_code_col: self.trial_info['step_code'],
                kn.mr_trial_arm_code_col: self.trial_info['arm_code'] if 'arm_code' in self.trial_info else None,
                kn.mr_trial_dose_code_col: self.trial_info['dose_code'] if 'dose_code' in self.trial_info else None,
            }

            trial_match_doc = {
                kn.tm_sample_id_col: sample[kn.sample_id_col],
                kn.tm_trial_protocol_no_col: self.trial_info['protocol_no'],
                kn.tm_mrn_col: sample[kn.mrn_col],
                kn.tm_vital_status_col: sample[kn.vital_status_col],
                kn.tm_trial_accrual_status_col: self.trial_info['accrual_status'],
                kn.tm_sort_order_col: 0,
                kn.tm_match_reasons_col: match_reasons
            }
            trial_match_docs.append(trial_match_doc)

        # todo add versioning
        res = self.db.trial_match.insert_many(trial_match_docs)
        logging.info('%s | %d trial matches added' % (self.trial_info['protocol_no'], len(res.inserted_ids)))

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
