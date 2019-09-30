FROM registry:latest 

RUN apk --update add tzdata \
    && rm -rf /etc/docker/registry/config.yml

COPY config.yml /etc/docker/registry/

CMD ["/etc/docker/registry/config.yml"]