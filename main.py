from ebs_snapshots import ebs_snapshots_daemon
import sys
import kayvee

if __name__ == "__main__":
    try:
        ebs_snapshots_daemon.snapshot_timer()
    except Exception as e:
        print kayvee.formatLog("ebs-snapshots", "error", "unknown exception", {"error": str(e)})
        sys.exit(1)
