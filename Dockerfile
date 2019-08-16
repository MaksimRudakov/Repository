FROM python:latest

WORKDIR /

COPY req.txt /
RUN pip install --no-cache-dir requests docker docker-registry-client pyyaml

ADD docker_registries_sync.py /docker_registries_sync.py

CMD /bin/sh
# CMD ["python", "-u" "docker_registries_sync.py"]