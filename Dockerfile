FROM ubuntu:latest

RUN apt-get update && DEBIAN_FRONTEND=noninteractive apt-get install -y \
    python3.8 \
    python3-pip \
    python3-setuptools \
    build-essential

WORKDIR /app
COPY . /app

RUN python3.8 -m pip install --upgrade pip virtualenv setuptools wheel && \
    pip3 install -r /app/requirements.txt

EXPOSE 8080

ENTRYPOINT ["/app/docker-entrypoint.sh"]
