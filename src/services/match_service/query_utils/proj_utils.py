from src.utilities import settings as s
from src.data_store import key_names as kn
from src.services.match_service.query_utils.clinical_utils import ClinicalUtils
from src.services.match_service.query_utils.genomic_utils import GenomicUtils


class ProjUtils(ClinicalUtils, GenomicUtils):

    def __init__(self):
        ClinicalUtils.__init__(self)
        GenomicUtils.__init__(self)

        self.proj_col_dict = {
            s.mt_diagnosis: self.diagnosis_key
        }
        self.proj = {
            '_id': 0,
            kn.sample_id_col: 1,
            kn.mrn_col: 1,
            kn.vital_status_col: 1
        }

    def create_clinical_proj(self, key):
        """
        Create MongoDB projection to return only the matching diagnosis from the sample record.

        :param key {str}
        :return: {null}
        """
        self.proj[self.proj_col_dict[key]] = 1
