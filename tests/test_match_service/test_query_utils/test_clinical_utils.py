import datetime as dt

from tests.test_match_service import TestQueryUtilitiesShared
from src.services.match_service.query_utils.clinical_utils import ClinicalUtils
from src.utilities.settings import oncotree_all_solid_text, oncotree_all_liquid_text


class TestClinicalUtils(TestQueryUtilitiesShared):

    def setUp(self):
        super(TestClinicalUtils, self).setUp()

        self.c = ClinicalUtils()

    def tearDown(self):
        pass

    def test_text_from_node(self):

        res = self.c._text_from_node(nodes=['NSCLC'])
        assert res == ['Non-Small Cell Lung Cancer'], res

    def test_expand_oncotree_diagnosis(self):

        diagnoses = self.c.expand_oncotree_diagnosis(diagnosis='Non-Small Cell Lung Cancer')
        assert sorted(diagnoses) == sorted(self.all_nsclc_cancer_types), sorted(diagnoses)

    def test_expand_grouped_diagnoses(self):

        all_liquid_cancers = self.c.expand_grouped_diagnoses(diagnosis=oncotree_all_liquid_text)
        all_solid_cancers = self.c.expand_grouped_diagnoses(diagnosis=oncotree_all_solid_text)
        assert sorted(all_liquid_cancers) == self.all_liquid_cancer_types, sorted(all_liquid_cancers)
        assert sorted(all_solid_cancers) == self.all_solid_cancer_types, sorted(all_solid_cancers)

    def test_convert_age_to_birth_date_subquery(self):

        q1 = self.c.convert_age_to_birth_date_subquery(age_str='<=18')
        q2 = self.c.convert_age_to_birth_date_subquery(age_str='>=18')
        q3 = self.c.convert_age_to_birth_date_subquery(age_str='<18')
        q4 = self.c.convert_age_to_birth_date_subquery(age_str='>18')
        q5 = self.c.convert_age_to_birth_date_subquery(age_str='>.5')

        assert q1.keys() == ['$gte']
        assert q2.keys() == ['$lte']
        assert q3.keys() == ['$gt']
        assert q4.keys() == ['$lt']
        assert q5.keys() == ['$lt']
        assert type(q1['$gte']) == dt.datetime
        assert type(q2['$lte']) == dt.datetime
        assert type(q3['$gt']) == dt.datetime
        assert type(q4['$lt']) == dt.datetime
        assert type(q5['$lt']) == dt.datetime

    def test_get_months(self):

        today = dt.datetime.today().replace(year=2016, month=11, day=3)

        # The return of "get_months" provides the month to replace and the years to subtract from today's date
        months_, year = self.c._get_months(age=".5", today=today)
        assert months_ == 5, months_
        assert year == 0, year

        months_, year = self.c._get_months(age=".25", today=today)
        assert months_ == 8, months_
        assert year == 0, year

        months_, year = self.c._get_months(age="1.5", today=today)
        assert months_ == 5, months_
        assert year == 1, year

        months_, year = self.c._get_months(age="10.25", today=today)
        assert months_ == 8, months_
        assert year == 10, year

        # A special use case is if subtracting months from today's date causes the date to proceed into the previous
        # year. At this point, we set today to February and assert that the correct math is applied.
        today = today.replace(month=2)
        months_, year = self.c._get_months(age=".5", today=today)
        assert months_ == 8, months_
        assert year == -1, year

        months_, year = self.c._get_months(age="10.25", today=today)
        assert months_ == 11, months_
        assert year == -11, year
