from ebs_snapshots.s3_backup_config import S3BackupConfig
import unittest
import yaml
import boto
from moto import mock_s3

access_key = "fake"
secret_key = "fake"


class TestS3BackupConfig(unittest.TestCase):

    @mock_s3
    def test_can_initialize(self):
        # if key doesn't exist, initialization should still succeed in case key
        # is written after daemon is started
        b = S3BackupConfig(
            "s3://fake-bucket/fake-backup-conf.yml", access_key, secret_key)

    @mock_s3
    def test_refresh_errors_when_key_does_not_exist(self):
        conn = boto.connect_s3()
        bucket = conn.create_bucket('fake-bucket')
        k = boto.s3.key.Key(bucket)

        b = S3BackupConfig(
            "s3://fake-bucket/does-not-exist.yml", access_key, secret_key)
        with self.assertRaises(boto.exception.S3ResponseError):
            b.refresh()

    @mock_s3
    def test_refresh_errors_if_cannot_parse_yaml(self):
        conn = boto.connect_s3()
        bucket = conn.create_bucket('fake-bucket')
        k = boto.s3.key.Key(bucket)
        k.key = "not-valid-yaml.yml"
        k.set_contents_from_filename("test/not-valid-yaml.yml")

        b = S3BackupConfig(
            "s3://fake-bucket/not-valid-yaml.yml", access_key, secret_key)
        with self.assertRaises(yaml.scanner.ScannerError):
            b.refresh()
        b = S3BackupConfig(
            "s3://fake-bucket/not-valid-yaml.yml", access_key, secret_key)

    @mock_s3
    def test_get_data(self):
        conn = boto.connect_s3()
        bucket = conn.create_bucket('fake-bucket')
        k = boto.s3.key.Key(bucket)
        k.key = "example-volumes.yml"
        k.set_contents_from_filename("test/example-volumes.yml")

        b = S3BackupConfig(
            "s3://fake-bucket/example-volumes.yml", access_key, secret_key)
        data = b.get()
        self.assertEqual(len(data), 3)
        self.assertEquals(
            data['vol-1'], {'interval': 'yearly', 'max_snapshots': 0})
        self.assertEquals(
            data['vol-2'], {'interval': 'monthly', 'max_snapshots': 1})
        self.assertEquals(
            data['vol-3'], {'interval': 'hourly', 'max_snapshots': 2})
