from src.utilities import settings as s
from src.data_store import key_names as kn

from src.services.match_service.query_utils.query_utils import QueryUtils
from src.services.match_service.query_utils.clinical_utils import ClinicalUtils


class ClinicalQueries(QueryUtils, ClinicalUtils):

    def __init__(self):
        ClinicalUtils.__init__(self)
        QueryUtils.__init__(self)

    def create_oncotree_diagnosis_query(self, cancer_type, include=True):
        """
        Create MongoDB query to find records by oncotree diagnosis name

        :param cancer_type {str}
        :param include: {bool}
        :return: {dict}
        """
        if cancer_type in [s.oncotree_all_solid_text, s.oncotree_all_liquid_text]:
            expanded_diagnoses = self.expand_grouped_diagnoses(diagnosis=cancer_type)
        else:
            expanded_diagnoses = self.expand_oncotree_diagnosis(diagnosis=cancer_type)

        return {kn.oncotree_primary_diagnosis_name_col: {self.list_inclusion_dict[include]: expanded_diagnoses}}

    def create_age_query(self, age):
        """
        Create MongoDB query to find records by birth date

        :param age: {str} (e.g. ">=17")
        :return: {dict}
        """
        # todo unit test
        subquery = self.convert_age_to_birth_date_subquery(age_str=age)
        return {kn.birth_date_col: subquery}

    @staticmethod
    def create_gender_query(gender):
        """
        Create MongoDB query to find records by gender

        :param gender: {str} (e.g. "Male", "Female")
        :return: {dict}
        """
        # todo unit test
        return {kn.gender_col: {'$eq': gender}}
