import unittest
import json
import os
from backup_manager import BackupManager


class TestBackupManager(unittest.TestCase):

    def test_instance_is_singleton(self):
        a = BackupManager.instance()
        b = BackupManager.instance()
        assert a is b

    def test_registering_volumes(self):
        b = BackupManager()
        b.register_volume(
            'vol-fake1234', {'interval': 'hourly', 'max_snapshots': 5})
        # b.register_volume('vol-fake5678', 'hourly', 5)
        actual = b.get_volumes()
        expected = {
            'vol-fake1234': {
                'interval': 'hourly',
                'max_snapshots': 5,
            }
        }
        self.assertEquals(actual, expected)

        b.deregister_volume('vol-fake1234')
        actual = b.get_volumes()
        expected = {}
        self.assertEquals(actual, expected)


    def test_loads_volumes_from_file(self):
        b = BackupManager()
        b.load_config_from_file('test/example-volumes.yml')
        volumes = b.get_volumes()
        self.assertEquals(len(volumes), 3)
        self.assertEquals(volumes['vol-1'], {'interval': 'yearly', 'max_snapshots': 0})
        self.assertEquals(volumes['vol-2'], {'interval': 'monthly', 'max_snapshots': 1})
        self.assertEquals(volumes['vol-3'], {'interval': 'hourly', 'max_snapshots': 2})

