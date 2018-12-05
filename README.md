# ebs-snapshots

`ebs-snapshots` allows you to create and clean up AWS EBS snapshots according to a schedule.

(Thanks for `skymill` for the basis of this work: https://github.com/skymill/automated-ebs-snapshots)

## Usage

This requires a valid AWS session (see go/iam).

```
AWS_REGION=your_region \
AWS_BACKUP_REGION=your_backup_region \
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
AWS_REGION             # AWS Region, e.g. us-west-1
AWS_BACKUP_REGION	   # AWS Region for backups, e.g. us-west-2
BACKUP_CONFIG          # Path to backup config. May be local file or s3 path (see "Configuration")
```

### Optional: Running in Docker

Build the docker image:

```
docker build --tag=local/ebs-snapshots $(pwd)
```

Run as a docker container, making sure to specify required env vars:

```
docker run \
-e AWS_REGION=$AWS_REGION \
-e BACKUP_CONFIG=$BACKUP_CONFIG \
local/ebs-snapshots
```

## Testing

```
make test
```

