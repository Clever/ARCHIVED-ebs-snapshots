from ebs_snapshots.file_backup_config import FileBackupConfig
import unittest
import yaml
from jsonschema import ValidationError


class TestFileBackupConfig(unittest.TestCase):

    def test_can_initialize(self):
        b = FileBackupConfig("test/example-volumes.yml")

    def test_errors_on_invalid_file(self):
        b = FileBackupConfig("test/does-not-exist.yml")
        with self.assertRaises(IOError):
            b.refresh()

    def test_errors_if_cannot_parse_yaml(self):
        b = FileBackupConfig("test/not-valid-yaml.yml")
        with self.assertRaises(yaml.scanner.ScannerError):
            b.refresh()

    def test_get_data(self):
        b = FileBackupConfig("test/example-volumes.yml")
        data = b.get()
        self.assertEqual(len(data), 3)
        self.assertEquals(
            data['vol-1'], {'interval': 'yearly', 'max_snapshots': 0})
        self.assertEquals(
            data['vol-2'], {'interval': 'monthly', 'max_snapshots': 1})
        self.assertEquals(
            data['vol-3'], {'interval': 'hourly', 'max_snapshots': 2})

    def test_errors_on_invalid_config(self):
        with self.assertRaises(AssertionError):
            FileBackupConfig._validate_config("")

        with self.assertRaises(ValidationError):
            FileBackupConfig._validate_config({"some_other": "dict"})

    def test_valid_config(self):
        config = {
            "vol-fake1111": {"max_snapshots": 5, "interval": "daily"},
            "vol-fake2222": {"interval": "hourly"},
            "vol-fake3333": {"max_snapshots": 3},
            "vol-fake4444": {},
        }
        FileBackupConfig._validate_config(config)
