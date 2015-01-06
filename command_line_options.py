""" Command line options """
import argparse

parser = argparse.ArgumentParser(
    description='Automatic AWS EBS snapshot handling')
aws_config_ag = parser.add_argument_group(
    title='AWS configuration options')
aws_config_ag.add_argument(
    '--access-key-id',
    help='AWS access key')
aws_config_ag.add_argument(
    '--secret-access-key',
    help='AWS secret access key')
aws_config_ag.add_argument(
    '--region',
    default='us-east-1',
    help='AWS region. Default: us-east-1')

args = parser.parse_args()
