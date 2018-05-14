import ebs_snapshots.snapshot_manager as snapshot_manager
import unittest
from mock import MagicMock
import boto
from moto import mock_ec2

class TestSnapshotManager(unittest.TestCase):

    @mock_ec2
    def test_ignore_attached_volumes(self):
        conn = boto.connect_ec2()

        # create a volumes
        volume = conn.create_volume(50, 'us-west-1a')

        # mock out details for snapshot_manager.run
        snapshot_manager._ensure_snapshot = MagicMock()
        snapshot_manager._remove_old_snapshots = MagicMock()

        # run function for volume
        snapshot_manager.run(conn, volume.id, 'daily', 0, '')
        self.assertEqual(1, snapshot_manager._ensure_snapshot.call_count)
        self.assertEqual(2, snapshot_manager._remove_old_snapshots.call_count)
