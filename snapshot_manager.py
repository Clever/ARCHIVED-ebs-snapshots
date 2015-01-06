""" Module handling the snapshots """
import datetime
import yaml
from boto.exception import EC2ResponseError
from valid_intervals import VALID_INTERVALS


# TODO: this interface could be volume specific instead
# id, interval, max_snapshots
def run(connection, volume_id, interval='daily', max_snapshots=0):
    """ Ensure that we have snapshots for a given volume

    :type connection: boto.ec2.connection.EC2Connection
    :param connection: EC2 connection object
    :returns: None
    """
    try:
      volumes = connection.get_all_volumes([volume_id])
    except EC2ResponseError as error:
      print('ERROR: failed to connect to AWS: {}'.format(error.message))
      return
    
    for volume in volumes:
        _ensure_snapshot(connection, volume, interval)
        _remove_old_snapshots(connection, volume, max_snapshots)


def _create_snapshot(volume):
    """ Create a new snapshot

    :type volume: boto.ec2.volume.Volume
    :param volume: Volume to snapshot
    :returns: boto.ec2.snapshot.Snapshot -- The new snapshot
    """
    print('Creating new snapshot for {}'.format(volume.id))
    snapshot = volume.create_snapshot(
        description="Automatic snapshot by Automated EBS Snapshots")
    print('Created snapshot {} for volume {}'.format(
        snapshot.id, volume.id))

    return snapshot


def _ensure_snapshot(connection, volume, interval):
    """ Ensure that a given volume has an appropriate snapshot

    :type connection: boto.ec2.connection.EC2Connection
    :param connection: EC2 connection object
    :type volume: boto.ec2.volume.Volume
    :param volume: Volume to check
    :returns: None
    """
    if interval not in VALID_INTERVALS:
        print(
            'WARNING: "{}" is not a valid snapshotting interval for volume {}'.format(
                interval, volume.id))
        return

    snapshots = connection.get_all_snapshots(filters={'volume-id': volume.id})

    # Create a snapshot if we don't have any
    if not snapshots:
        _create_snapshot(volume)
        return

    min_delta = 3600*24*365*10  # 10 years :)
    for snapshot in snapshots:
        timestamp = datetime.datetime.strptime(
            snapshot.start_time,
            '%Y-%m-%dT%H:%M:%S.000Z')
        delta_seconds = int(
            (datetime.datetime.utcnow() - timestamp).total_seconds())

        if delta_seconds < min_delta:
            min_delta = delta_seconds

    print('The newest snapshot for {} is {} seconds old'.format(
        volume.id, min_delta))
   
    if interval == 'hourly' and min_delta > 3600:
        _create_snapshot(volume)
    elif interval == 'daily' and min_delta > 3600*24:
        _create_snapshot(volume)
    elif interval == 'weekly' and min_delta > 3600*24*7:
        _create_snapshot(volume)
    elif interval == 'monthly' and min_delta > 3600*24*30:
        _create_snapshot(volume)
    elif interval == 'yearly' and min_delta > 3600*24*365:
        _create_snapshot(volume)
    else:
        print('No need for a new snapshot of {}'.format(volume.id))


def _remove_old_snapshots(connection, volume, max_snapshots):
    """ Remove old snapshots

    :type connection: boto.ec2.connection.EC2Connection
    :param connection: EC2 connection object
    :type volume: boto.ec2.volume.Volume
    :param volume: Volume to check
    :returns: None
    """
    retention = max_snapshots
    if not type(retention) is int and retention >= 0:
        print( 
            'WARNING: "{}" is not a valid value for max_snapshots for volume {}'.format(
                retention, volume.id))
        return
    snapshots = connection.get_all_snapshots(filters={'volume-id': volume.id})

    # Sort the list based on the start time
    snapshots.sort(key=lambda x: x.start_time)

    # Remove snapshots we want to keep
    snapshots = snapshots[:-int(retention)]

    if not snapshots:
        print('No old snapshots to remove')
        return

    for snapshot in snapshots:
        print('Deleting snapshot {}'.format(snapshot.id))
        try:
            snapshot.delete()
        except EC2ResponseError as error:
            print('WARNING: Could not remove snapshot: {}'.format(
                error.message))

    print('Done deleting snapshots')
