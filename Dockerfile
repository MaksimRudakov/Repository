FROM alpine:latest

RUN apk update
RUN apk add py-pip
RUN apk add ca-certificates
RUN rm -rf /var/cache/apk/* 
RUN pip install --no-cache-dir requests docker docker-registry-client pyyaml

COPY certs/* /certs/
COPY certs/ca.crt /usr/local/share/ca-certificates/ca.crt
COPY start.sh /
COPY docker_registries_sync.py /

RUN update-ca-certificates

ENV REQUESTS_CA_BUNDLE=/certs/ca.crt

CMD sh start.sh

