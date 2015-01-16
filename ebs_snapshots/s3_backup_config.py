import yaml
from backup_config import BackupConfig
import kayvee
from boto import connect_s3
import boto
from urlparse import urlparse


class S3BackupConfig(BackupConfig):

    config = {}
    path = ""

    def __init__(self, path, aws_access_key_id, aws_secret_access_key):
        self.path = path
        self.access_key = aws_access_key_id
        self.secret_key = aws_secret_access_key

    def refresh(self):
        """ Read s3 path and return parsed yml """
        # Get data from s3
        s3_connection = connect_s3(self.access_key, self.secret_key)
        s3_bucket = urlparse(self.path).hostname
        s3_path = urlparse(self.path).path[1:]  # no leading /
        bucket = s3_connection.lookup(s3_bucket)
        k = boto.s3.key.Key(bucket)
        k.key = s3_path
        s = k.get_contents_as_string()

        # Update backup config
        return yaml.load(s)
