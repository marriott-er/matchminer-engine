import re


class GenomicUtils:

    def __init__(self):
        pass

    @staticmethod
    def regex_compile_gene_name(gene_name):
        """
        Converts the gene name into a compiled regex object

        :param gene_name: {str}
        :return: {regex object}
        """
        return re.compile("(.*\W{0}\W.*)|(^{0}\W.*)|(.*\W{0}$)".format(gene_name), re.IGNORECASE)
