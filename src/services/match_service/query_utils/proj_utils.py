from src.utilities import settings as s
from src.data_store import key_names as kn
from src.services.match_service.query_utils.clinical_utils import ClinicalUtils
from src.services.match_service.query_utils.genomic_utils import GenomicUtils


class ProjUtils(ClinicalUtils, GenomicUtils):

    def __init__(self):
        ClinicalUtils.__init__(self)
        GenomicUtils.__init__(self)

        self.clinical_inclusion_dict = {
            True: self.create_clinical_inclusion_proj,
            False: self.create_clinical_exclusion_proj
        }
        self.clinical_proj_dict = {
            s.mt_diagnosis: self.diagnosis_key,
            s.mt_age: self.age_key,
            s.mt_gender: self.gender_key
        }
        self.proj = {
            '_id': 0,
            kn.sample_id_col: 1,
            kn.mrn_col: 1,
            kn.vital_status_col: 1
        }
        self.exclusion_key = 'ne'

    def create_clinical_proj(self, include=True, **kwargs):
        """
        Create MongoDB projection to return only the matching diagnosis from the sample record.

        :param include {bool}
        :param kwargs
        :return: {null}
        """
        proj = self.proj.copy()
        subproj = self.clinical_inclusion_dict[include](**kwargs)
        for k, v in proj.iteritems():
            subproj[k] = v

        return proj

    def create_clinical_inclusion_proj(self, **kwargs):
        """
        Create MongoDB projection to return only the matching diagnosis from the sample record.

        :param kwargs:
            - key {str]

        :return: {null}
        """
        return {self.clinical_proj_dict[k]: 1 for k in kwargs['keys']}

    def create_clinical_exclusion_proj(self, **kwargs):
        """
        Return indicator that matching records matched because they lacked the specified criteria

        :param kwargs:
            - keys {list str}
            - vals {list any type}

        :return: {null}
        """
        return {self.clinical_proj_dict[k]: v for k, v in zip(kwargs['keys'], kwargs['vals'])}
