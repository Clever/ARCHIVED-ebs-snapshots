from backup_config import BackupConfig
import yaml
import json


class InlineBackupConfig(BackupConfig):

    config = {}
    path = ""

    def __init__(self, path):
        """ Try loading path as inline YAML, then JSON """
        try:
            self.config = yaml.load(path)
        except:
            try:
                self.config = json.loads(path)
            except:
                raise ValueError("BACKUP_CONFIG is not valid yaml or json")

        # ensure config is valid
        self._validate_config(self.config)

    def refresh(self):
        """ no-op """
        return self.config
