from backup_config import BackupConfig
import yaml
import jsonschema
import kayvee


class FileBackupConfig(BackupConfig):

    config = {}
    path = ""

    def __init__(self, path):
        self.path = path

    def refresh(self):
        """ Read file and return parsed yml """
        with open(self.path, "r") as open_file:
            return yaml.load(open_file)
