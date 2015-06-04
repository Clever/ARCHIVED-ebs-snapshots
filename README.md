# ebs-snapshots

`ebs-snapshots` allows you to create and clean up AWS EBS snapshots according to a schedule.

(Thanks for `skymill` for the basis of this work: https://github.com/skymill/automated-ebs-snapshots)

## Usage

```
AWS_ACCESS_KEY=your_key \
AWS_SECRET_KEY=your_secret \
AWS_REGION=your_region \
BACKUP_CONFIG=s3://your-bucket/snapshots-config.yml \
python main.py
```

This starts a long-running process that will take snapshots according to the config file.

`BACKUP_CONFIG` may be a local file, an s3 path, or inline YAML/JSON.

### Configuration

Configuration files are written in [yaml](http://www.yaml.org/) (a superset of JSON) format.
Top level keys are volume ids. These map to a dict of parameters:

- `interval` - frequency of snapshots: hourly, daily, monthly, yearly
- `max_snapshots` - max snapshots to keep, 0 keeps all
- `name` - name of snapshot, written to EC2 tag 'Name"

Here is an example configuration file to automate snapshots for two volumes:

```yaml
vol-fake1234:
  interval: daily
  max_snapshots: 0
  name: Fake database
vol-fake5678:
  interval: hourly
  max_snapshots: 48
```

### Required Env

You must specify these env vars in order to connect to AWS and to choose the configuration file.

```
AWS_ACCESS_KEY  # Your AWS Credentials
AWS_SECRET_KEY  # Your AWS Credentials
AWS_REGION      # AWS Region, e.g. us-west-1
CONFIG_PATH     # Path to backup config. May be local file or s3 path (see "Configuration")
```

### AWS Policy

You'll need to grant the proper IAM permissions to the AWS credentials you're using.

1. ec2 volume, snapshot, and tag, permissions - to create snapshots of volumes and tag them
1. s3 bucket permissions - allows reading your config file from an s3 path

See the included [example policy](aws-iam-policy.ebs-snapshots.json).

### Optional: Running in Docker

Build the docker image:

```
docker build --tag=local/ebs-snapshots $(pwd)
```

Run as a docker container, making sure to specify required env vars:

```
docker run \
-e AWS_ACCESS_KEY_ID=$AWS_ACCESS_KEY_ID \
-e AWS_SECRET_ACCESS_KEY=$AWS_SECRET_ACCESS_KEY \
-e AWS_REGION=$AWS_REGION \
-e BACKUP_CONFIG=$BACKUP_CONFIG \
local/ebs-snapshots
```

## Testing

```
make test
```

