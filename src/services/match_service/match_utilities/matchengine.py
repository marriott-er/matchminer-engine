import networkx as nx

from src.utilities import settings as s
from src.data_store import key_names as kn
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
        for node_id in list(nx.dfs_postorder_nodes(self.match_tree_nx, source=1)):
            node = self.match_tree_nx.node[node_id]
            if node['type'] == 'clinical':
                subquery = self._assess_genomic_node(node=node)
            elif node['type'] == 'genomic':
                subquery = self._assess_genomic_node(node=node)

    def _assess_clinical_node(self, node):
        """
        Assess the given node and construct the appropriate MongoDB query.

        :param node: {digraph node}
        :return: {dict}
        """
        criteria = sorted(node['value'].keys())

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
            variant_category = self._normalize_variant_category_val(node['value'][s.mt_variant_category])
            include = self._assess_inclusion(node_value=variant_category)

            # Structural Variants
            if variant_category == s.variant_category_sv_val:
                return self.create_sv_query(gene_name=gene_name, include=include)

            # Mutations and CNVs
            else:
                return self.create_gene_level_query(gene_name=gene_name,
                                                    variant_category=variant_category,
                                                    include=include)
        # variant-level mutation criteria
        elif s.mt_protein_change in criteria:
            gene_name = node['value'][s.mt_hugo_symbol]
            protein_change = node['value'][s.mt_protein_change]
            variant_category = self._normalize_variant_category_val(node['value'][s.mt_variant_category])
            include = self._assess_inclusion(node_value=variant_category)
            return self.create_mutation_query(gene_name=gene_name,
                                              protein_change=protein_change,
                                              include=include)
        # wildcard-level mutation criteria
        elif s.mt_wc_protein_change in criteria:
            gene_name = node['value'][s.mt_hugo_symbol]
            protein_change = node['value'][s.mt_wc_protein_change]
            variant_category = self._normalize_variant_category_val(node['value'][s.mt_variant_category])
            include = self._assess_inclusion(node_value=variant_category)
            return self.create_wildcard_query(gene_name=gene_name,
                                              protein_change=protein_change,
                                              include=include)
        # exon-level mutation criteria
        elif s.mt_exon in criteria:
            gene_name = node['value'][s.mt_hugo_symbol]
            exon = node['value'][s.mt_exon]
            variant_category = self._normalize_variant_category_val(node['value'][s.mt_variant_category])
            include = self._assess_inclusion(node_value=variant_category)
            return self.create_exon_query(gene_name=gene_name,
                                          exon=exon,
                                          include=include)
        # cnv criteria
        elif s.mt_cnv_call in criteria:
            gene_name = node['value'][s.mt_hugo_symbol]
            cnv_call = node['value'][s.mt_cnv_call]
            variant_category = self._normalize_variant_category_val(node['value'][s.mt_variant_category])
            include = self._assess_inclusion(node_value=variant_category)
            return self.create_cnv_query(gene_name=gene_name,
                                         cnv_call=cnv_call,
                                         include=include)

        # mutational signature criteria
        elif any([criterion in s.mt_signature_cols for criterion in criteria]):
            for sig in s.mt_signature_cols:
                sigtype, sigval = self._normalize_signature_vals(signature_type=sig, signature_val=node['value'][sig])
                # todo is there such a thing as signature exclusion criteria?
                # todo is there such a thing as non MMR/MS Status signature curation?

        # low-coverage criteria
        # todo build out low coverage criteria logic



    @staticmethod
    def _assess_inclusion(node_value):
        """
        Assess if the given node value sholud be treated as an inclusion or an exclusion criterion.
        If it begins with "!" treat as an exclusion criterion. Otherwise, treat as an inclusion criterion.

        :param node_value: {str}
        :return: {bool} True if inclusion, False if exclusion
        """
        return not node_value.startswith('!')

    @staticmethod
    def _normalize_variant_category_val(val):
        """
        Normalize the variant category value to what is expected in the samples table in the database.

        :param val: {str}
        :return: {str}
        """
        variant_category_dict = {
            s.mt_cnv_val: s.variant_category_cnv_val,
            s.mt_mut_val: s.variant_category_mutation_val,
            s.mt_sv_val: s.variant_category_sv_val
        }
        return variant_category_dict[val]

    @staticmethod
    def _normalize_cnv_call_val(val):
        """
        Normalize the cnv call value to what is expected in the samples table in the database.

        :param val: {str}
        :return: {str}
        """
        cnv_call_dict = {
            s.mt_high_amp_val: s.cnv_call_high_amp,
            s.mt_homo_del_val: s.cnv_call_homo_del,
            s.mt_hetero_del_val: s.cnv_call_hetero_del,
            s.mt_low_amp_val: s.cnv_call_gain
        }
        return cnv_call_dict[val]

    @staticmethod
    def _normalize_signature_vals(signature_type, signature_val):
        """
        Normalize the mutational signature type and value to what is expected in the samples table in the database.

        :param signature_type: {str} (e.g. mmr_status, ms_status, etc.)
        :param signature_val: {str} (e.g. (MMR-Deficient, MSI-H, etc.)
        :return: {tuple of str} (type, val)
        """
        signature_type_dict = {
            s.mt_mmr_status: kn.mmr_status_col,
            s.mt_ms_status: kn.ms_status_col
        }
        signature_val_dict = {
            s.mt_mmr_deficient_val: s.mmr_status_deficient_val,
            s.mt_mmr_proficient_val: s.mmr_status_proficient_val,
            s.mt_msi_high_val: s.ms_status_msih_val,
            s.mt_mss_val: s.ms_status_mss_val
        }
        return signature_type_dict[signature_type], signature_val_dict[signature_val]

    def search_for_matching_records(self):
        raise NotImplementedError
