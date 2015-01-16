# Automated EBS Snapshots
FROM python:2.7.8

# Install python deps
ADD requirements.txt ./
RUN pip install -r requirements.txt

# Add application files
ADD . ./

# Run
CMD ["./run.sh"]
