from flask import Flask
from flask.ext.restful import Api
from backup_manager import BackupManager
from perpetual_timer import PerpetualTimer
from api_resources import VolumeList, Volume
from command_line_options import args
import connection_manager

app = Flask(__name__)
api = Api(app)


def main():
    b = BackupManager.instance()

    # set AWS config, pulled from command line arguments
    b.aws_config = dict(
        access_key_id=args.access_key_id,
        secret_access_key=args.secret_access_key,
        region=args.region,
    )

    # allow loading base backup configuration from a file
    b.load_config_from_file("volumes.yml")

    # call the background thread 5 seconds 
    def handle_snapshots():
        BackupManager.instance().run()
    t = PerpetualTimer(5, handle_snapshots)
    t.start()

    # start api, which allows modifying backup configuration
    api.add_resource(VolumeList, '/volumes')
    api.add_resource(Volume, '/volumes/<volume_id>')

    # TODO: allow setting PORT and DEBUG from env
    app.run(port=5001)

if __name__ == "__main__":
    main()
