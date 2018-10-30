class Variants:

    def __init__(self):
        pass

    def create_mutation_object(self, data):
        """
        Create a mutation object from the given old_data

        :param data: {dict}
        :return: {dict}
        """
        raise NotImplementedError

    def create_cnv_object(self, data):
        """
        Create a cnv object from the given old_data

        :param data: {dict}
        :return: {dict}
        """
        raise NotImplementedError

    def create_sv_object(self, data):
        """
        Create a sv object from the given old_data

        :param data: {dict}
        :return: {dict}
        """
        raise NotImplementedError

    def determine_signature_type(self, data):
        """
        Determine signature type from the old_data

        :param data: {list of mixed type}
        :return: {str}
        """
        raise NotImplementedError

    def split_mmr_status(self, mmr_status):
        """
        Split CAMD MMR Status text into MS Status and MMR Status

        :param mmr_status: {str}
        :return: {tuple}
        """
        raise NotImplementedError
