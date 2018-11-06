from src.data_store import key_names as kn


from src.services.match_service.query_utilities.query_utilities import QueryUtilities
from src.services.match_service.query_utilities.clinical_utilities import ClinicalUtilities


class ClinicalQueries(QueryUtilities, ClinicalUtilities):

    def __init__(self):
        ClinicalUtilities.__init__(self)
        QueryUtilities.__init__(self)

    def create_oncotree_diagnosis_query(self, cancer_type, include=True):
        """
        Create MongoDB query to find records by oncotree diagnosis name

        :param cancer_type {str}
        :param include: {bool}
        :return: {dict}
        """
        expanded_diagnoses = self.expand_oncotree_diagnosis(diagnosis=cancer_type)
        return {kn.oncotree_primary_diagnosis_name_col: {self.list_inclusion_dict[include]: expanded_diagnoses}}

    def create_age_query(self, include=True):
        """
        Create MongoDB query to find records by birth date

        :param include: {bool}
        :return: {dict}
        """
        raise NotImplementedError

    def create_gender_query(self, include=True):
        """
        Create MongoDB query to find records by gender

        :param include: {bool}
        :return: {dict}
        """
        raise NotImplementedError
