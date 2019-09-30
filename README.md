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


# Конфиг для контейнера-синхронизации

```
# Ресстр источник
source_registry:
  url: https://images.boston.loc
  # username: some_user
  # password: some_password

# Конечный реестр
destination_registry:
  url: https://images.dallas.loc

# Взять все репозитории из реестра
# Если False то нужно указать список в repositories
take_all_repositories: True

# Фильтр префиксов
prefixes: False

# Репозитории для синхронизации
repositories:
  # - registry
  - python

# Префиксы, которые ищутся в тегах для дальнейшей синхронизации
prefix:
  - "p_"

# Удаление репозиториев
delete_repositories: False
```