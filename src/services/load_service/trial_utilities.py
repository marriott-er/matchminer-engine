import os
import yaml
import subprocess


class TrialUtilities:

    def __init__(self, db):

        self.db = db
        self.load_dict = {
            'yml': self.yaml_to_mongo,
            'bson': self.bson_to_mongo,
            'json': self.json_to_mongo
        }

    def yaml_to_mongo(self, yml):
        """
        If you specify the path to a directory, all files with extension YML will be added to MongoDB.
        If you specify the path to a specific YML file, it will add that file to MongoDB.

        :param yml: Path to YML file.
        """

        # search directory for ymls
        if os.path.isdir(yml):
            for y in os.listdir(yml):
                ymlpath = os.path.join(yml, y)

                # only add files of extension ".yml"
                if ymlpath.split('.')[-1] != 'yml':
                    continue

                # convert yml to json format
                add_trial(ymlpath, self.db)
        else:
            add_trial(yml, self.db)

    @staticmethod
    def bson_to_mongo(bson):
        """
        If you specify the path to a directory, all files with extension BSON will be added to MongoDB.
        If you specify the path to a specific BSON file, it will add that file to MongoDB.

        :param bson: Path to BSON file.
        """
        cmd = "mongorestore --host localhost:27017 --db matchminer %s" % bson
        subprocess.call(cmd.split(' '))

    @staticmethod
    def json_to_mongo(json):
        """
        If you specify the path to a directory, all files with extension JSON will be added to MongoDB.
        If you specify the path to a specific JSON file, it will add that file to MongoDB.

        :param json: Path to JSON file.
        """
        cmd = "mongoimport --host localhost:27017 --db matchminer --collection trial --file %s" % json
        subprocess.call(cmd.split(' '))


def add_trial(yml, db):
    """
    Adds file in YAML format to MongoDB

    :param yml: Path to file
    :param db: MongoDB connection
    """

    with open(yml) as f:
        t = yaml.load(f.read())
        db.trial.insert_one(t)
