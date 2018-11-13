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

        self.genomic_inclusion_dict = {
            True: self.create_genomic_inclusion_proj,
            False: self.create_genomic_exclusion_proj
        }
        self.genomic_proj_dict = {
            s.mt_hugo_symbol: self.hugo_symbol_key
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
        Return either inclusive or exclusive clinical projetion.

        :param include {bool}
        :param kwargs
        :return: {dict}
        """
        subproj = self.clinical_inclusion_dict[include](**kwargs)
        if not include:
            return subproj

        proj = self.proj.copy()
        for k, v in subproj.iteritems():
            proj[k] = v

        return proj

    def create_clinical_inclusion_proj(self, **kwargs):
        """
        Create MongoDB projection to return only the matching diagnosis from the sample record.

        :param kwargs:
            - keys {list of str}

        :return: {dict}
        """
        return {self.clinical_proj_dict[k]: 1 for k in kwargs['keys']}

    def create_clinical_exclusion_proj(self, **kwargs):
        """
        Return indicator that matching records matched because they lacked the specified criteria

        :param kwargs:
            - keys {list of str}
            - vals {list of any type}

        :return: {dict}
        """
        return {self.clinical_proj_dict[k]: v for k, v in zip(kwargs['keys'], kwargs['vals'])}

    def create_genomic_proj(self, include=True, **kwargs):
        """
        Return either inclusive or exclusive genomic projetion.

        :param include: {bool}
        :param kwargs:
        :return: {dict}
        """
        subproj = self.genomic_inclusion_dict[include](**kwargs)
        if not include:
            return subproj

        proj = self.proj.copy()
        for k, v in subproj.iteritems():
            proj[k] = v

        return proj

    @staticmethod
    def create_genomic_inclusion_proj(**kwargs):
        """
        Create MongoDB projection to return only the matching genomic variants from the sample record.

        :param kwargs:
            - query {dict}

        :return: {dict}
        """
        return kwargs['query']

    def create_genomic_exclusion_proj(self, **kwargs):
        """
        Return indicator that matching records matched because they lacked the specified criteria

        :param kwargs:
            - keys {list of str}
            - vals {list of any type}

        :return: {dict}
        """
        proj = {}
        for k, v in zip(kwargs['keys'], kwargs['vals']):
            if v is None:
                continue
            elif k in self.genomic_proj_dict:
                proj[self.genomic_proj_dict[k]] = v
            else:
                proj[k] = v

        return proj
