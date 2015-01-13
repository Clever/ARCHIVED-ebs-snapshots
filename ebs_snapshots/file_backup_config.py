from backup_config import BackupConfig
import yaml
import kayvee

class FileBackupConfig(BackupConfig):

    config = {}
    path = ""

    def __init__(self, path):
        self.path = path

    def refresh(self):
        """ Read file and update BackupConfig """
        with open(self.path, "r") as open_file:
            self.config = yaml.load(open_file)

    def get(self):
        """ Get a dict of BackupConfig items """
        try:
            self.refresh()
        except Exception as e:
            print kayvee.formatLog("ebs-snapshots", "warning", "unable to load backup config", {"path": self.path, "error": str(e)})
        return self.config
