# docker_registries_sync

# Команда для старта реестра:
docker run -d --restart=always --name images.boston.loc \
    #  Папка с сертификатами
    
    -v /cephfs/DEV/sync_registries/certs/images.boston.loc/certs:/certs \
    # Папка хранилище
    
    -v /path/data:/var/lib/local \
    # Говорит реестру работать на 443 порту
    
    -e REGISTRY_HTTP_ADDR=0.0.0.0:443 \
    # Указатели на сертификаты
    
    -e REGISTRY_HTTP_TLS_CERTIFICATE=/certs/domain.crt \
    -e REGISTRY_HTTP_TLS_KEY=/certs/domain.key \
    -p 443:443 \
    registry:2


# Команда для старта регистрации:
docker run --rm \
    # Ссылка на docker на хосте
    
    -v /var/run/docker.sock:/var/run/docker.sock
    # Конфиг реестра
    
    -v $(pwd)/config.yml:/config.yml \
    sync
