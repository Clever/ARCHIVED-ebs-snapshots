""" Handles connections to AWS """
import sys

from boto import ec2
from boto.utils import get_instance_metadata


def connect_to_ec2(region='us-east-1', access_key=None, secret_key=None):
    """ Connect to AWS ec2

    :type region: str
    :param region: AWS region to connect to
    :type access_key: str
    :param access_key: AWS access key id
    :type secret_key: str
    :param secret_key: AWS secret access key
    :returns: boto.ec2.connection.EC2Connection -- EC2 connection
    """
    print 'INFO: Connecting to AWS EC2 in {}'.format(region)

    if access_key:
        # Connect using supplied credentials
        connection = ec2.connect_to_region(
            region,
            aws_access_key_id=access_key,
            aws_secret_access_key=secret_key)
    else:
        # Fetch instance metadata
        metadata = get_instance_metadata(timeout=1, num_retries=1)
        if metadata:
            try:
                region = metadata['placement']['availability-zone'][:-1]
            except KeyError:
                pass

        # Connect using env vars or boto credentials
        connection = ec2.connect_to_region(region)

    if not connection:
        print "ERROR: failed to connect to ec2" 
        sys.exit(1)

    return connection
