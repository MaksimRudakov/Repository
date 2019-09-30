FROM alpine:latest

RUN apk update \
    && apk add py-pip \
    && apk add ca-certificates \
    && rm -rf /var/cache/apk/* \
    && pip install --no-cache-dir requests docker docker-registry-client pyyaml

COPY certs/* /certs/
COPY certs/ca.crt /usr/local/share/ca-certificates/ca.crt
COPY docker_registries_sync.py /

RUN update-ca-certificates

ENV REQUESTS_CA_BUNDLE=/certs/ca.crt

CMD ["python", "docker_registries_sync.py"]

