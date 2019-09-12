FROM ubuntu:latest

WORKDIR /

RUN apt-get update \
    && apt-get install -y docker \
    && apt-get install -y python-pip \
    && pip install --no-cache-dir requests docker docker-registry-client pyyaml

# Если нужно добавить незащищенный репозиторий
# COPY daemon.json /etc/docker/
# Можно копировать конфиг внутрь контейнера или передать при старте через --volumes (-v)
# COPY config.yml /
COPY docker_registries_sync.py /
COPY start.sh /
COPY certs/images.boston.loc/certs/* /certs/

CMD /bin/sh /start.sh
