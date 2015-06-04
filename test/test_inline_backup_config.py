import unittest

from ebs_snapshots.inline_backup_config import InlineBackupConfig
import unittest
import yaml
from jsonschema import ValidationError

VALID = open("test/example-volumes.yml", 'r').read()
VALID_JSON = open("test/valid.json", 'r').read()
INVALID_SCHEMA = open("test/invalid-schema.yml", 'r').read()
INVALID_SCHEMA_JSON = open("test/invalid-schema.json", 'r').read()

class TestInlineBackupConfig(unittest.TestCase):

    def test_can_initialize(self):
        b = InlineBackupConfig(VALID)

    def test_errors_on_invalid_config(self):
        # the colon char ":" is used to check if it's JSON or YAML
        # so this config is both invalid YAML and invalid JSON
        with self.assertRaises(ValueError):
            b = InlineBackupConfig(":")

    def test_get_data(self):
        b = InlineBackupConfig(VALID)
        data = b.get()
        self.assertEqual(len(data), 3)
        self.assertEquals(
            data['vol-1'], {'interval': 'yearly', 'max_snapshots': 0})
        self.assertEquals(
            data['vol-2'], {'interval': 'monthly', 'max_snapshots': 1})
        self.assertEquals(
            data['vol-3'], {'interval': 'hourly', 'max_snapshots': 2})

    def test_errors_when_valid_yml_but_invalid_schema(self):
        with self.assertRaises(ValidationError):
          b = InlineBackupConfig(INVALID_SCHEMA)

    def test_errors_when_valid_json_but_invalid_schema(self):
        with self.assertRaises(ValidationError):
          b = InlineBackupConfig(INVALID_SCHEMA)
