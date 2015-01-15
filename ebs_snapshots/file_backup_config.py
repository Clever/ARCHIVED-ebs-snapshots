from backup_config import BackupConfig
import yaml
import jsonschema
import kayvee

schema = {
    "type": "object",
    "name": "Volume backup schedule",
    "properties": {
            "max_snapshots": {"type": "number"},
            "interval": {"type": "string"},
    },
    "additionalProperties": False,
}

class FileBackupConfig(BackupConfig):

    config = {}
    path = ""

    def __init__(self, path):
        self.path = path

    def refresh(self):
        """ Read file and return parsed yml """
        with open(self.path, "r") as open_file:
            return yaml.load(open_file)

    @classmethod
    def _validate_config(cls, new_config):
        """ Raises exception if config loaded from file doesn't match expected schema """
        assert type(new_config) is dict
        for key, val in new_config.iteritems():
            jsonschema.validate(val, schema)
    
    def get(self):
        """ Get a dict of config items """
        try:
            new_config = self.refresh()
            self._validate_config(new_config)
            self.config = new_config
        except Exception as e:
            print kayvee.formatLog("ebs-snapshots", "warning", "unable to load backup config", {"path": self.path, "error": str(e)})
        
        return self.config
