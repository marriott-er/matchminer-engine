"""Copyright 2016 Dana-Farber Cancer Institute"""

import logging
import pandas as pd

from src.data_store import key_names as kn

logging.basicConfig(level=logging.DEBUG, format='[%(levelname)s] %(message)s', )


class Sort:

    def __init__(self, trial_matches):
        self.trial_matches = trial_matches

        self.trial_matches_df = None
        self.all_sample_ids = None
        self.f_alive = None
        self.f_open = None
        self.f_no_svs = None

    def prep_trial_matches(self):
        """
        Add columns to dataframe to facilitate sorting

        :return: {null}
        """
        self.trial_matches_df = pd.DataFrame.from_dict(self.trial_matches)

        self.trial_matches_df['has_mut'] = self.trial_matches_df[kn.mutation_list_col].apply(self._has_vc)
        self.trial_matches_df['has_cnv'] = self.trial_matches_df[kn.cnv_list_col].apply(self._has_vc)
        self.trial_matches_df['has_sv'] = self.trial_matches_df[kn.sv_list_col].apply(self._has_vc)
        self.trial_matches_df['has_wt'] = self.trial_matches_df[kn.wt_genes_col].apply(self._has_vc)

        self.all_sample_ids = self.trial_matches_df[kn.sample_id_col].unique().tolist()
        self.f_alive = (self.trial_matches_df[kn.vital_status_col] == 'alive')
        self.f_open = (self.trial_matches_df[kn.tm_trial_accrual_status_col] == 'open')
        self.f_no_svs = (self.trial_matches_df['has_sv'] == False)


def add_sort_order(trial_matches):
    """
    Aggregate all the trial matches by MRN and provide a sort order using the following logic:
    (1) First sort by tier
    (2) Then sort by match_type (variant > gene)
    (3) Then sort by cancer type (specific cancer type > all solid/liquid)
    (4) Then sort by coordinating center (DFCI > MGH)
    (5) Then sort by reverse protocol number (high > low)

    :param trial_matches: List of trial match dictionaries
    :return: List of trial match dictionaries with sort_order column filled in:
    """
    # todo unit test
    if len(trial_matches) == 0:
        return trial_matches

    s = Sort(trial_matches=trial_matches)
    s.prep_trial_matches()

    master_sort_order = {}
    for sample_id in s.all_sample_ids:
        f_sample_id = (s.trial_matches_df[kn.sample_id_col] == sample_id)
        df = s.trial_matches_df[s.f_alive & s.f_open & s.f_no_svs & f_sample_id]
        matches = df.T.to_dict().values()

        # The sort order dictionary keeps track of the priority for each sort category for each match
        # Index 0 is sorted by tier with values 0 to 7
        # Index 1 is sorted by match type with values 0 to 1
        # Index 2 is sorted by cancer type match with values 0 to 2
        # Index 3 is sorted by coordinating center with values 0 to 1
        # Index 4 is sorted by reverse protocol number
        sort_order = {}

        for match in matches:

            idx = (match[kn.sample_id_col], match[kn.tm_trial_protocol_no_col])
            if idx not in sort_order:
                sort_order[idx] = []

            sort_order = sort_by_tier(match, sort_order)
            sort_order = sort_by_match_type(match, sort_order)
            sort_order = sort_by_cancer_type(match, sort_order)
            sort_order = sort_by_coordinating_center(match, sort_order)

        sort_order = sort_by_reverse_protocol_no(matches, sort_order)
        master_sort_order = final_sort(sort_order, master_sort_order)

    s.trial_matches_df['sort_order'] = s.trial_matches_df.apply(
        lambda x: master_sort_order[(x[kn.sample_id_col], x[kn.tm_trial_protocol_no_col])]
        if (x[kn.sample_id_col], x[kn.tm_trial_protocol_no_col]) in master_sort_order
        else -1, axis=1)

    return s.trial_matches_df.to_json(orient='records', date_format='iso')


def sort_by_match_type(match, sort_order):
    """
    Second highest priority sorting
    """
    # todo unit test
    idx = (match[kn.sample_id_col], match[kn.tm_trial_protocol_no_col])

    if 'match_type' in match and match['match_type'] == 'variant':
        sort_order[idx] = add_sort_value(sort_value=0,
                                         priority=1,
                                         sort_order_li=sort_order[idx])

    elif 'match_type' in match and match['match_type'] == 'gene':
        sort_order[idx] = add_sort_value(sort_value=1,
                                         priority=1,
                                         sort_order_li=sort_order[idx])
    else:
        sort_order[idx] = add_sort_value(sort_value=2,
                                         priority=1,
                                         sort_order_li=sort_order[idx])

    return sort_order


def sort_by_cancer_type(match, sort_order):
    """
    Third highest priority sorting
    """

    idx = (match[kn.sample_id_col], match[kn.tm_trial_protocol_no_col])

    if 'cancer_type_match' in match and match['cancer_type_match'] == 'specific':
        sort_order[idx] = add_sort_value(sort_value=0,
                                         priority=2,
                                         sort_order_li=sort_order[idx])

    elif 'cancer_type_match' in match and match['cancer_type_match'] == 'all_solid':
        sort_order[idx] = add_sort_value(sort_value=1,
                                         priority=2,
                                         sort_order_li=sort_order[idx])

    elif 'cancer_type_match' in match and match['cancer_type_match'] == 'all_liquid':
        sort_order[idx] = add_sort_value(sort_value=1,
                                         priority=2,
                                         sort_order_li=sort_order[idx])

    else:
        sort_order[idx] = add_sort_value(sort_value=2,
                                         priority=2,
                                         sort_order_li=sort_order[idx])

    return sort_order


def sort_by_coordinating_center(match, sort_order):
    """
    Fourth highest priority sorting
    """
    # todo unit test
    idx = (match[kn.sample_id_col], match[kn.tm_trial_protocol_no_col])

    if 'coordinating_center' in match and match['coordinating_center'] == 'Dana-Farber Cancer Institute':
        sort_order[idx] = add_sort_value(sort_value=0,
                                         priority=3,
                                         sort_order_li=sort_order[idx])
    else:
        sort_order[idx] = add_sort_value(sort_value=1,
                                         priority=3,
                                         sort_order_li=sort_order[idx])

    return sort_order


def sort_by_reverse_protocol_no(matches, sort_order):
    """
    Lowest priority sorting
    """
    # todo unit test
    rev_prot_no_sort = sorted(matches, key=lambda k: int(k[kn.tm_trial_protocol_no_col].split('-')[0]))
    i = 0

    for match in rev_prot_no_sort[::-1]:

        if len(sort_order[(match[kn.sample_id_col], match[kn.tm_trial_protocol_no_col])]) == 4:
            sort_order[(match[kn.sample_id_col], match[kn.tm_trial_protocol_no_col])].append(i)
            i += 1

    return sort_order


def final_sort(sort_order, master_sort_order):
    # todo unit test
    cols = ['tier', 'match_type', 'cancer_type', 'coordinating_center', 'rev_protocol_no']
    sort_order_df = pd.DataFrame(sort_order.values(), columns=cols, index=sort_order.keys())
    sort_order_df.sort_values(by=cols, axis=0, ascending=True, inplace=True)

    j = 0
    for idx, row in sort_order_df.iterrows():
        master_sort_order[idx] = j
        j += 1

    return master_sort_order


# --------- #
# Utilities #
# --------- #
def has_vc(vc):
    """
    Assess if row has variants in the given variant category

    :param vc: {list or null}
    :return: {bool or null}
    """
    return len(vc) > 0 if isinstance(vc, list) else vc


def add_sort_value(sort_value, priority, sort_order_li):
    """
    Adds the sort value, independent of the logic required to assess and determine that value.
    Accepts the lowest sort_value when there are multiple matches.

    :param sort_value: Integer value that determines sort order
    :param priority: Integer that determines which column to assign the sort value
        (e.g. tier, match_type, etc.)
    :param sort_order_li: The match-specific sort order list so far
    """
    if len(sort_order_li) >= priority + 1:

        if sort_value < sort_order_li[priority]:
            sort_order_li[priority] = sort_value
    else:
        sort_order_li.append(sort_value)

    return sort_order_li


def extract_tier(match):
    """
    Extract tier from mutation list

    :param match: {dict}
    :return: {int or null}
    """
    if kn.mutation_list_col not in match or len(match[kn.mutation_list_col]) == 0:
        return None

    tiers = [i[kn.tier_col] for i in match[kn.mutation_list_col]
             if kn.tier_col in i and i[kn.tier_col] is not None]
    return min(tiers) if len(tiers) > 0 else None


# --------------- #
# Sorting methods #
# --------------- #
def sort_by_tier(match, sort_order):
    """
    Highest priority sorting
    Signatures > Tier 1 mutations > Tier 2 mutations > CNVs > Tier 3 mutations > Tier 4 mutations > Wild-type

    :return {dict of lists}
    """
    idx = (match[kn.sample_id_col], match[kn.tm_trial_protocol_no_col])
    lowest_tier = extract_tier(match)

    if kn.mmr_status_col in match and pd.notnull(match[kn.mmr_status_col]):
        sort_order[idx] = add_sort_value(sort_value=0,
                                         priority=0,
                                         sort_order_li=sort_order[idx])

    elif lowest_tier == 1:
        sort_order[idx] = add_sort_value(sort_value=1,
                                         priority=0,
                                         sort_order_li=sort_order[idx])

    elif lowest_tier == 2:
        sort_order[idx] = add_sort_value(sort_value=2,
                                         priority=0,
                                         sort_order_li=sort_order[idx])

    elif kn.cnv_list_col in match and len(match[kn.cnv_list_col]) > 0:
        sort_order[idx] = add_sort_value(sort_value=3,
                                         priority=0,
                                         sort_order_li=sort_order[idx])

    elif lowest_tier == 3:
        sort_order[idx] = add_sort_value(sort_value=4,
                                         priority=0,
                                         sort_order_li=sort_order[idx])

    elif lowest_tier == 4:
        sort_order[idx] = add_sort_value(sort_value=5,
                                         priority=0,
                                         sort_order_li=sort_order[idx])

    elif kn.wt_genes_col in match and len(match[kn.wt_genes_col]):
        sort_order[idx] = add_sort_value(sort_value=6,
                                         priority=0,
                                         sort_order_li=sort_order[idx])

    else:
        sort_order[idx] = add_sort_value(sort_value=7,
                                         priority=0,
                                         sort_order_li=sort_order[idx])

    return sort_order
