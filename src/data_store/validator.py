from cerberus import Validator

from src.data_store.data_model import samples_schema


def validate_document(doc):
    """
    Validate the given document with the matchengine samples schema

    :param doc: {dict}
    :return: {boolean} True if passed validation
    """
    v = Validator(samples_schema)
    return v.validate(doc)
