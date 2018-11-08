from src.utilities import settings as s
from src.data_store import key_names as kn


class ClinicalProjs:

    def __init__(self):
        pass

    @staticmethod
    def create_oncotree_diagnosis_proj(proj):
        """
        Create MongoDB projection to return only the matching diagnosis from the sample record.

        :param proj {dict}
        :return: {dict}
        """
        proj[kn.oncotree_primary_diagnosis_name_col] = 1
        return proj
