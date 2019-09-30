# docker_registries_sync

# Команда для старта реестра:
```
docker run -d --restart=always --name images.dallas.loc \
    # Папка хранилище, там же серты
    -v /cephfs/docker-repo1:/var/lib/registry \
    -e "TZ=Asia/Almaty" \
    -p 443:443 \
    registry.2
```


# Команда для старта контейнера с скриптом синхронизации:
```
docker run --rm \
    # Ссылка на docker на хосте
    -v /var/run/docker.sock:/var/run/docker.sock
    # Конфиг реестра
    -v $(pwd)/config.yml:/config.yml \
    sync
```
