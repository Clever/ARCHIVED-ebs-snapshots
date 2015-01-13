from ebs_snapshots import ebs_snapshots_daemon

if __name__ == "__main__":
    pid_file = '/tmp/automatic-ebs-snapshots.pid'
    daemon = ebs_snapshots_daemon.EbsSnapshotsDaemon(pid_file)
    daemon.run()
