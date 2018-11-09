import datetime as dt
import networkx as nx
import oncotreenx as ox

from src.utilities import settings as s
from src.data_store import key_names as kn


class ClinicalUtils(object):

    def __init__(self):
        self.oncotree = ox.build_oncotree(file_path=s.TUMOR_TREE)
        self.age_query_dict = {
            '>=': '$lte',
            '<=': '$gte',
            '>': '$lt',
            '<': '$gt'
        }

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

    def convert_age_to_birth_date_subquery(self, age_str):
        """
        Convert age to datetime object of the birth date.

        :param age_str: {str}
        :return: {dict}
        """
        today = dt.datetime.today()

        # parse operator and age from string
        if age_str[1] == '=':
            idx = 2
        else:
            idx = 1

        operator = age_str[:idx]
        age = age_str[idx:]
        if '.' in age:
            month, year = self._get_months(age=age, today=today)
            birth_dt = today.replace(month=month, year=(today.year + year))
        else:
            try:
                birth_dt = today.replace(year=today.year - int(age))
            except ValueError:
                birth_dt = today + (dt.datetime(today.year + int(age), 1, 1) - dt.datetime(today.year, 1, 1))

        return {self.age_query_dict[operator]: birth_dt}

    @staticmethod
    def _get_months(age, today):
        """
        Given a decimal, returns the number of months and number of years to subtract from today

        :param age: {str}
        :param today: {datetime object}
        :return {tuple} (month {int}, year {int})
        """
        split_age = str(age).split('.')

        # month
        month = split_age[1]
        month = int((float(month) * 12) / (10 ** len(month)))  # e.g. convert 5/10 to x/12

        # year
        if split_age[0] == '':
            year = 0
        else:
            year = int(split_age[0])

        # handle crossing over a year boundary
        months = [
            'January', 'February', 'March', 'April', 'May', 'June',
            'July', 'August', 'September', 'October', 'November', 'December'
        ]
        if today.month - month <= 0:
            month = months.index(months[-(abs(today.month - month))])
            year = -(year + 1)
        else:
            month = today.month - month

        if month == 0:
            month = 1

        return month, year
