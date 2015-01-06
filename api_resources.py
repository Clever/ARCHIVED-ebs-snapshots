from backup_manager import BackupManager 
from flask.ext.restful import reqparse, abort, Resource

BACKUPS = BackupManager.instance()

parser = reqparse.RequestParser()
parser.add_argument('volume', type=str)
parser.add_argument('max_snapshots', type=int)
parser.add_argument('interval', type=str)

def abort_if_volume_doesnt_exist(volume_id):
    if volume_id not in BACKUPS.config:
        abort(404, message="Volume {} doesn't exist".format(volume_id))

# Volume
class Volume(Resource):
    def get(self, volume_id):
        abort_if_volume_doesnt_exist(volume_id)
        return BACKUPS.config[volume_id]

    def delete(self, volume_id):
        abort_if_volume_doesnt_exist(volume_id)
        BACKUPS.deregister_volume(volume_id)
        return '', 204

    def put(self, volume_id):
        args = parser.parse_args()
        print args
        params = dict(
            max_snapshots=args['max_snapshots'],
            interval=args['interval']
        )
          
        BACKUPS.register_volume(volume_id, params)

        print "registered"
        return BACKUPS.config[volume_id], 201

# VolumeList
class VolumeList(Resource):
    def get(self):
        return BACKUPS.config

    def post(self):
        print "POST"
        args = parser.parse_args()
        print args
        params = dict(
            max_snapshots=args['max_snapshots'],
            interval=args['interval']
        )
        print params
        BACKUPS.register_volume(args['volume'], params)
        print "registered"
        print BACKUPS.config
        return BACKUPS.config[args['volume']], 201

