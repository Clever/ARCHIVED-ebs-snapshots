from ebs_snapshots import ebs_snapshots_daemon
import sys
import kayvee
import logging
logging.basicConfig(level=logging.INFO)

if __name__ == "__main__":
    try:
        ebs_snapshots_daemon.run_once()
    except Exception as e:
        logging.error(kayvee.formatLog("ebs-snapshots", "error", "unknown exception", {"error": str(e)}))
        sys.exit(1)
