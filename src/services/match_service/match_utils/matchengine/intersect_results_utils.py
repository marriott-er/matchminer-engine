from src.utilities import settings as s
from src.data_store import key_names as kn


class IntersectResultsUtils(object):

    def __init__(self):
        self.intersection_dict = {'and': set.intersection_update, 'or': set.update}
        self.clinical_keys = [kn.oncotree_primary_diagnosis_name_col, kn.birth_date_col, kn.gender_col]
        self.genomic_keys = [
            'genomic_exclusion_reasons',
            'clinical_exclusion_reasons',
            kn.mutation_list_col,
            kn.cnv_list_col,
            kn.sv_list_col,
            kn.wt_genes_col
        ]

    def intersect_results(self, node, children):
        """
        Intersect match results by sample id.

        :param node: {digraph node}
        :param children: {list of digraph nodes}
        :return: {digraph node}
        """
        # todo unit test
        matched_sample_ids = self._get_sample_ids(node=children[0])
        node['matches'] = self._get_matches(node=children[0])
        for child in children[1:]:

            # intersect/update current set of matched sample ids with child's
            child_matched_sample_ids = self._get_sample_ids(node=child)
            self.intersection_dict[node['type']](matched_sample_ids, child_matched_sample_ids)

            # remove any matches filtered out by the previous step
            node['matches'] = self._filter_matches(node=node, sample_ids=matched_sample_ids)
            old_sample_ids = self._get_sample_ids(node=node)

            # iterate each of this child's matches and update accordingly
            for child_match in child['matches'][:]:
                child_sample_id = child_match[kn.sample_id_col]
                if child_sample_id not in matched_sample_ids:
                    continue

                # when the match already exists, we check the child's match to see if reasons need to be added
                if child_match[kn.sample_id_col] in old_sample_ids:
                    old_match = self._filter_matches(node=node, sample_ids=[child_sample_id])[0]

                    # update clinical and signature reasons
                    self._update_old_match(old_match=old_match, child_match=child_match,
                                           keys=self.clinical_keys + s.signature_cols)

                    # update genomic reasons
                    self._update_old_match(old_match=old_match, child_match=child_match,
                                           keys=self.genomic_keys, genomic=True)

                # or we add new matches as appropriate
                else:
                    node['matches'].extend(self._filter_matches(node=child, sample_ids=matched_sample_ids))

    @staticmethod
    def _get_sample_ids(node):
        """
        Retrieve a set of unique sample ids from the given node.

        :param node: {digraph node}
        :return: {set}
        """
        # todo unit test
        return set(i[kn.sample_id_col] for i in node['matches'])

    @staticmethod
    def _get_matches(node):
        """
        Retrieve a list of matched records from the given node.

        :param node: {digraph node}
        :return: {list of dict}
        """
        # todo unit test
        return node['matches'][:]

    @staticmethod
    def _filter_matches(node, sample_ids):
        """
        Filter matches in the given node by the given set of sample ids

        :param node: {digraph node}
        :param sample_ids: {set}
        :return: {list}
        """
        # todo unit test
        return [i for i in node['matches'] if i[kn.sample_id_col] in sample_ids]

    @staticmethod
    def _update_old_match(old_match, child_match, keys, genomic=False):
        """
        Update the old match with information from the child match if applicable.

        :param old_match: {dict}
        :param child_match: {dict}
        :param keys: {list of str}
        :param genomic: {bool}
        :return: {dict} (old_match)
        """
        # todo unit test
        for key in keys:
            if key in child_match and key not in old_match:
                old_match[key] = child_match[key]
            elif genomic and key in child_match and key in old_match:
                if isinstance(old_match[key], dict):
                    old_match[key] = [old_match[key]]
                old_match[key].append(child_match[key])

        return old_match
