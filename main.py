from ebs_snapshots import ebs_snapshots_daemon
import sys
import kayvee
import logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    try:
        ebs_snapshots_daemon.snapshot_timer()
    except Exception as e:
        logging.error(kayvee.formatLog("ebs-snapshots", "error", "unknown exception", {
            "error": str(e),
            "_kvmeta": {
                "team": "eng-infra",
                "kv_version": "2.0.2",
                "kv_language": "python",
                "routes": [ {
                    "type": "notifications",
                    "channel": "#oncall-infra",
                    "icon": ":camera_with_flash:",
                    "user": "ebs-snapshots",
                    "message": "ERROR: " + str(e),
                } ]
            }
        }))
        sys.exit(1)
