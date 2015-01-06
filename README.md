# ebs-snapshots

Create and clean up Amazon EBS snapshots according to a schedule.

## Usage

Run once from command line:

```
python client.py --access-key-id=$AWS_ACCESS_KEY --secret-access-key=$AWS_SECRET_KEY --region=$AWS_REGION --s3file=$PATH
```

Run as a service:

```
python client.py --access-key-id=$AWS_ACCESS_KEY --secret-access-key=$AWS_SECRET_KEY --region=$AWS_REGION --s3file=$PATH
```

## Configuration

Here is an example configuration for two volumes to be snapshotted. Each specifies the volume id,
frequency of snapshots, and maximum number of snapshots to keep.

```yaml
vol-fake1234:       # volume id
  interval: daily   # frequency of snapshots: hourly, daily, monthly, yearly
  max_snapshots: 7  # max snapshots to keep, 0 keeps all
vol-fake5678:
  interval: hourly 
  max_snapshots: 48 
```

## Testing

```
make test
```
