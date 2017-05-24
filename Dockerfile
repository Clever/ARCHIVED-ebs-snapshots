# Automated EBS Snapshots
FROM python:2.7

# Certificates needed for https requests, to avoid
# "x509: failed to load system roots and no roots provided" error
RUN apt-get update -y && \
    apt-get install -y ca-certificates curl && \
    curl -L https://github.com/Clever/batchcli/releases/download/0.0.12/batchcli-v0.0.12-linux-amd64.tar.gz | tar xz -C /usr/local/bin --strip-components 1 && \
    apt-get -y remove curl && \
    apt-get -y autoremove

# Install Python deps
ADD requirements.txt ./
RUN pip install -r requirements.txt && \
    rm -rf /tmp/* /var/tmp/*

# Add application files
ADD . ./

# Run
CMD ["batchcli", "--cmd", "/usr/bin/python", "/main.py"]
