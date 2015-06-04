import jsonschema
import kayvee
import logging

schema = {
    "type": "object",
    "name": "Volume backup schedule",
    "properties": {
            "max_snapshots": {"type": "number"},
            "interval": {"type": "string"},
            "name": {"type": "string"},
    },
    "additionalProperties": False,
}


class BackupConfig:

    """
    Interface shared by backup configs

    Config items are dicts, with key equal to the volume id mapped to a dict of
    parameters

    {
        "vol-1234567" : {
            "interval": "daily",
            "max_snapshots": 7,
            "name": "events-db",
            ...
        },
        ...
    }
    """

    path = None

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
            logging.warning(kayvee.formatLog("ebs-snapshots", "warning", "unable to load backup config", {"path": self.path, "error": str(e)}))

        return self.config

    def refresh(self):
      """ returns config dict, after being updated """
      raise NotImplementedError("refresh() must be implemented in subclasses")
