import networkx as nx
import oncotreenx as ox

from src.data_store import key_names as kn
from src.utilities import settings as s


class ClinicalUtilities(object):

    def __init__(self):
        self.oncotree = ox.build_oncotree(file_path=s.TUMOR_TREE)

    def _text_from_node(self, nodes):
        """
        Get text string value from each oncotree node

        :param nodes: {list of oncotree nodes}
        :return {list of str}
        """
        return list(set(self.oncotree.node[n]['text'] for n in nodes))

    def expand_oncotree_diagnosis(self, diagnosis):
        """
        Expand Oncotree Primary diagnosis text to include all of its children

        :param diagnosis: {str}
        :return: {list of str}
        """
        node = ox.lookup_text(self.oncotree, diagnosis)
        nodes = [node]

        # get its children.
        if self.oncotree.has_node(node):
            nodes.extend(list(nx.dfs_tree(self.oncotree, node)))

        return self._text_from_node(nodes=nodes)

    def expand_grouped_diagnoses(self, diagnosis):
        """
        Expand all solid or all liquid tumors to all oncotree values.
        All liquid tumors is defined as the set of diagnoses under "Blood" or "Lymph".
        All solid tumor is defined as the entire set of diagnoses minus this all liquid tumor set.

        :param diagnosis: {str} _LIQUID_ or _SOLID_
        :return: {list of str}
        """
        # build the nodes for liquid.
        lymph_node = ox.lookup_text(self.oncotree, "Lymph")
        blood_node = ox.lookup_text(self.oncotree, "Blood")

        lymph_nodes = list(nx.dfs_tree(self.oncotree, lymph_node))
        blood_nodes = list(nx.dfs_tree(self.oncotree, blood_node))
        liquid_nodes = list(set(lymph_nodes).union(set(blood_nodes)))

        if diagnosis == s.oncotree_all_liquid_text:
            return self._text_from_node(nodes=liquid_nodes)

        # solid nodes comprise the inverse
        if diagnosis == s.oncotree_all_solid_text:
            all_nodes = set(list(self.oncotree.nodes()))
            solid_nodes = list(all_nodes - set(liquid_nodes))
            return self._text_from_node(nodes=solid_nodes)
