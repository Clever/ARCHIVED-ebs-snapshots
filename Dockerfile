# Automated EBS Snapshots

# https://registry.hub.docker.com/_/python/
# TODO: use python2.7 image OR apt-get && 
FROM ubuntu:12.04

# Install linux packages
RUN apt-get -y update
RUN apt-get install -y -q python2.7-dev
RUN apt-get install -y -q python-pip
RUN apt-get install -y -q libxml2-dev libxslt-dev
RUN apt-get install -y -q git
RUN apt-get install -y -q software-properties-common python-software-properties wget

# Install python deps
RUN pip install -U pip
ADD requirements.txt ./
RUN pip install -r requirements.txt

# Add application files
ADD . ./

# Run
CMD ["./run.sh"]
