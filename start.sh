echo "192.168.80.73 chicago.loc images.boston.loc images.dallas.loc" >> /etc/hosts
export REQUESTS_CA_BUNDLE=/certs/domain.crt
python docker_registries_sync.py