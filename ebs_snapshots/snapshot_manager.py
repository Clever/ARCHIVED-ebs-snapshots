""" Module handling the snapshots """
import datetime
import yaml
import boto3
from boto.exception import EC2ResponseError
import kayvee
import logging

""" Configure the valid backup intervals """
VALID_INTERVALS = [
    u'hourly',
    u'daily',
    u'weekly',
    u'monthly',
    u'yearly']


def run(connection, backup_client, volume_id, interval='daily', max_snapshots=0, name=''):
    """ Ensure that we have snapshots for a given volume

    :type connection: boto.ec2.connection.EC2Connection
    :param connection: EC2 connection object for primary EBS region
    :type backup_client: boto3.EC2.Client
    :param backup_client: EC2 client for backup region
    :type volume_id: str
    :param volume_id: identifier for boto.ec2.volume.Volume
    :type max_snapshots: int
    :param max_snapshots: number of snapshots to keep (0 means infinite)
    :returns: None
    """
    try:
        volumes = connection.get_all_volumes([volume_id])
    except EC2ResponseError as error:
        logging.error(kayvee.formatLog("ebs-snapshots", "error", "failed to connect to AWS", {
            "msg": error.message,
            "_kvmeta": {
                "team": "eng-infra",
                "kv_version": "2.0.2",
                "kv_language": "python",
                "routes": [ {
                    "type": "notifications",
                    "channel": "#oncall-infra",
                    "icon": ":camera_with_flash:",
                    "user": "ebs-snapshots",
                    "message": "ERROR: " + str(error.message),
                } ]
            }
        }))
        return

    for volume in volumes:
        _ensure_snapshot(connection, backup_client, volume, interval, name)
        _remove_old_snapshots(connection, volume, max_snapshots)
        _remove_old_snapshot_backups(backup_client, volume.id, max_snapshots)

def _create_snapshot(connection, volume, name=''):
    """ Create a new snapshot

    :type volume: boto.ec2.volume.Volume
    :param volume: Volume to snapshot
    :returns: boto.ec2.snapshot.Snapshot -- The new snapshot
    """
    logging.info(kayvee.formatLog("ebs-snapshots", "info", "creating new snapshot", {"volume": volume.id}))
    snapshot = volume.create_snapshot(
        description="automatic snapshot by ebs-snapshots")
    if not name:
        name = '{}-snapshot'.format(volume.id)
    connection.create_tags(
        [snapshot.id], dict(Name=name, creator='ebs-snapshots'))
    logging.info(kayvee.formatLog("ebs-snapshots", "info", "created snapshot successfully", {
        "name": name,
        "volume": volume.id,
        "snapshot": snapshot.id
    }))
    return snapshot

def _availability_zone_to_region_name(zone):
    """Get the region_name from an availability zone by removing last letter

    :type zone: str
    :param zone: name of availability zone
    :returns  str -- the name of the region
    """
    return zone[:-1]

def _copy_snapshot(backup_client, volume, snapshot_id, name):
    """ Copy a snapshot to another region

    :type backup_client: boto3.EC2.Client
    :param backup_client: EC2 client for backup region
    :type volume: boto.ec2.volume.Volume
    :param volume: Volume that snapshot is of
    :type snapshot_id: str
    :param snapshot_id: identifier for boto.ec2.snapshot.Snapshot (the snapshot to copy)
    :returns: str -- the id of the copy
    """
    logging.info(kayvee.formatLog("ebs-snapshots", "info", "copying snapshot", {"volume": volume.id}))
    region = _availability_zone_to_region_name(volume.zone)
    response = backup_client.copy_snapshot(
        SourceRegion=region,
        SourceSnapshotId=snapshot_id,
        Encrypted=True,
        Description='copy of {}'.format(snapshot_id))#,
        # DryRun=True)
    backup_client.create_tags(
        Resources=[response["SnapshotId"]],
        Tags=[
            {"Key":"Name", 'Value':name},
            {"Key":"creator", 'Value':"ebs-snapshots"},
            {"Key":"snapshot_source", 'Value':snapshot_id},
            {"Key":"volume-id", 'Value':volume.id}
        ]
    )
    logging.info(kayvee.formatLog("ebs-snapshots", "info", "copied snapshot successfully", {
        "name": name,
        "volume": volume.id,
        "snapshot_source": snapshot_id,
        "snapshot_copy": response["SnapshotId"]
    }))

    return response["SnapshotId"]

def _ensure_snapshot(connection, backup_client, volume, interval, name):
    """ Ensure that a given volume has an appropriate snapshot

    :type connection: boto.ec2.connection.EC2Connection
    :param connection: EC2 connection object
    :type volume: boto.ec2.volume.Volume
    :param volume: Volume to check
    :returns: None
    """
    if interval not in VALID_INTERVALS:
        logging.warning(kayvee.formatLog("ebs-snapshots", "warning", "invalid snapshotting interval", {
            "volume": volume.id,
            "interval": interval
        }))
        return

    snapshots = connection.get_all_snapshots(filters={'volume-id': volume.id})

    # Create a snapshot if we don't have any
    if not snapshots:
        _create_snapshot(connection, volume, name)
        return

    #@TODO: create backup if we don't have any (ensure_backups?)

    min_delta = 3600 * 24 * 365 * 10  # 10 years :)

    latest_complete_snapshot_id = None
    min_complete_snapshot_delta = 3600 * 24 * 365 * 10

    for snapshot in snapshots:
        logging.info(kayvee.formatLog("ebs-snapshots", "info", 'snapshot', data={"snapshot": snapshot.status}))
        # Determine time since latest snapshot.
        timestamp = datetime.datetime.strptime(
            snapshot.start_time,
            '%Y-%m-%dT%H:%M:%S.000Z')
        delta_seconds = int(
            (datetime.datetime.utcnow() - timestamp).total_seconds())

        if delta_seconds < min_delta:
            min_delta = delta_seconds

        # Determine latest completed snapshot's id.
        if snapshot.status == "completed" and delta_seconds < min_complete_snapshot_delta:
            latest_complete_snapshot_id = snapshot.id
            min_complete_snapshot_delta = delta_seconds

    logging.info(kayvee.formatLog("ebs-snapshots", "info", 'The newest snapshot for {} is {} seconds old'.format(volume.id, min_delta), data={}))
    logging.info(kayvee.formatLog("ebs-snapshots", "info", 'The newest completed snapshot for {} is {} seconds old (snapshot {})'.format(volume.id, min_complete_snapshot_delta, latest_complete_snapshot_id), data={}))

    # Create snapshot if latest is older than interval.
    if interval == 'hourly' and min_delta > 3600:
        _create_snapshot(connection, volume, name)
    elif interval == 'daily' and min_delta > 3600*24:
        _create_snapshot(connection, volume, name)
    elif interval == 'weekly' and min_delta > 3600*24*7:
        _create_snapshot(connection, volume, name)
    elif interval == 'monthly' and min_delta > 3600*24*30:
        _create_snapshot(connection, volume, name)
    elif interval == 'yearly' and min_delta > 3600*24*365:
        _create_snapshot(connection, volume, name)
    else:
        logging.info(kayvee.formatLog("ebs-snapshots", "info", "no snapshot needed", {"volume": volume.id}))

    # Copy most recent completed snapshot if latest completed is older than interval.
    if interval == 'hourly' and min_complete_snapshot_delta > 3600:
        _copy_snapshot(backup_client, volume, latest_complete_snapshot_id, name)
    elif interval == 'daily' and min_complete_snapshot_delta > 3600*24:
        _copy_snapshot(backup_client, volume, latest_complete_snapshot_id, name)
    elif interval == 'weekly' and min_complete_snapshot_delta > 3600*24*7:
        _copy_snapshot(backup_client, volume, latest_complete_snapshot_id, name)
    elif interval == 'monthly' and min_complete_snapshot_delta > 3600*24*30:
        _copy_snapshot(backup_client, volume, latest_complete_snapshot_id, name)
    elif interval == 'yearly' and min_complete_snapshot_delta > 3600*24*365:
        _copy_snapshot(backup_client, volume, latest_complete_snapshot_id, name)
    else:
        logging.info(kayvee.formatLog("ebs-snapshots", "info", "no backup snapshot needed", {"volume": volume.id}))

def _remove_old_snapshot_backups(client, volume_id, max_snapshots):
    """ Remove old snapshot backups

    :type client: boto3.EC2.Client
    :param client: EC2 client object
    :type volume_id: str
    :param volume_id: ID of volume to check
    :returns: None
    """
    logging.info(kayvee.formatLog("ebs-snapshots", "info", "removing old snapshot backups", data={"volume":volume_id}))
    retention = max_snapshots
    if not type(retention) is int and retention >= 0:
        logging.warning(kayvee.formatLog("ebs-snapshots", "warning", "invalid max_snapshots value", {
            "volume": volume_id,
            "max_snapshots": retention
        }))
        return

    response = client.describe_snapshots(
        Filters=[{ "Name": "tag:volume-id", "Values":[volume_id] }]
    )
    snapshots = response["Snapshots"]


    # Sort the list based on the start time
    snapshots.sort(key=lambda x: x["StartTime"])

    # Remove snapshots we want to keep
    snapshots = snapshots[:-int(retention)]

    # if not snapshots:
    #     logging.info(kayvee.formatLog("ebs-snapshots", "info", "no old backup snapshots to remove", data={}))
    #     return

    ec2 = boto3.resource('ec2')
    for snapshotInfo in snapshots:
        snapshot = ec2.Snapshot(snapshotInfo["SnapshotId"])
        logging.info(kayvee.formatLog("ebs-snapshots", "info", "deleting snapshot", {"snapshot": snapshot.id}))
        try:
            snapshot.delete()
        except EC2ResponseError as error:
            logging.warning(kayvee.formatLog("ebs-snapshots", "warning", "could not remove snapshot", {
                "snapshot": snapshot.id,
                "msg": error.message
            }))

    logging.info(kayvee.formatLog("ebs-snapshots", "info", "done deleting snapshot backups", data={}))


def _remove_old_snapshots(connection, volume, max_snapshots):
    """ Remove old snapshots

    :type connection: boto.ec2.connection.EC2Connection
    :param connection: EC2 connection object
    :type volume: boto.ec2.volume.Volume
    :param volume: Volume to check
    :returns: None
    """
    logging.info(kayvee.formatLog("ebs-snapshots", "info", "removing old snapshots", data={"volume":volume}))

    retention = max_snapshots
    if not type(retention) is int and retention >= 0:
        logging.warning(kayvee.formatLog("ebs-snapshots", "warning", "invalid max_snapshots value", {
            "volume": volume.id,
            "max_snapshots": retention
        }))
        return
    snapshots = connection.get_all_snapshots(filters={'volume-id': volume.id})

    # Sort the list based on the start time
    snapshots.sort(key=lambda x: x.start_time)

    # Remove snapshots we want to keep
    snapshots = snapshots[:-int(retention)]

    if not snapshots:
        logging.info(kayvee.formatLog("ebs-snapshots", "info", "no old snapshots to remove", data={}))
        return

    for snapshot in snapshots:
        logging.info(kayvee.formatLog("ebs-snapshots", "info", "deleting snapshot", {"snapshot": snapshot.id}))
        try:
            snapshot.delete()
        except EC2ResponseError as error:
            logging.warning(kayvee.formatLog("ebs-snapshots", "warning", "could not remove snapshot", {
                "snapshot": snapshot.id,
                "msg": error.message
            }))

    logging.info(kayvee.formatLog("ebs-snapshots", "info", "done deleting snapshots", data={}))
