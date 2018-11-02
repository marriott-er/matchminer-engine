from cerberus import Validator


class SamplesValidator(Validator):

    def validate_document(self, doc):
        """
        Validate the given document with the matchengine samples schema

        :param doc: {dict}
        :return: {boolean} True if passed validation
        """
        return self.validate(doc)
