# ebs-snapshots

Create and clean up Amazon EBS snapshots according to a schedule.

(Thanks for `skymill` for the basis of this work: https://github.com/skymill/automated-ebs-snapshots)

## Usage

```
python main.py 
```

This starts long-running, daemonized process.

**Required Env**

```
AWS_ACCESS_KEY  # Your AWS Credentials
AWS_SECRET_KEY  # Your AWS Credentials
AWS_REGION      # AWS Region, e.g. us-west-1
CONFIG_PATH     # Path to backup config. May be local file or s3 path (see "Configuration" below)
```

### Dockerized 

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

## Configuration

Configuration files are written in `yaml` (a superset of JSON) format.
Top level keys are volume ids. These map to a dict of parameters:

- `interval` - frequency of snapshots: hourly, daily, monthly, yearly
- `max_snapshots` - max snapshots to keep, 0 keeps all

Here is an example configuration file to automate snapshots for two volumes: 

```yaml
vol-fake1234:
  interval: daily  
  max_snapshots: 7 
vol-fake5678:
  interval: hourly 
  max_snapshots: 48 
```

## Testing

```
make test
```

