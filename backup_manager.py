import snapshot_manager
import connection_manager
import yaml
import threading


class SingletonMixin(object):
    __singleton_lock = threading.Lock()
    __singleton_instance = None

    @classmethod
    def instance(cls):
        if not cls.__singleton_instance:
            with cls.__singleton_lock:
                if not cls.__singleton_instance:
                    cls.__singleton_instance = cls()
        return cls.__singleton_instance


class BackupManager(SingletonMixin):

    volumes = {}
    connection = None

    # Allow loading/saving volumes config from a file
    # TODO: allow from s3
    def load_config_from_file(self, f):
        self.volumes = yaml.load(open(f, "r"))

    def connect_to_ec2(self):
        region = self.aws_config.get('region')
        access_key_id = self.aws_config.get('access_key_id')
        secret_access_key = self.aws_config.get('secret_access_key')
        return connection_manager.connect_to_ec2(region, access_key_id, secret_access_key)

    def run(self):
        if not self.aws_config:
            print "no aws config"
            return
        
        connection = self.connect_to_ec2()
        for volume, params in self.volumes.iteritems():
          # default to daily snapshots without cleanup
          interval = params.get('interval', 'daily')
          max_snapshots = params.get('max_snapshots', 0)
          snapshot_manager.run(connection, volume, interval, max_snapshots) 

    def register_volume(self, volume_id, params={}):
        self.volumes[volume_id] = params

    def deregister_volume(self, volume_id):
        if self.volumes.has_key(volume_id):
            self.volumes.pop(volume_id)

    def get_volumes(self):
        return self.volumes
