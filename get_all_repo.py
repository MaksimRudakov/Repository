# -*- coding: utf-8 -*-
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import os
import yaml
import docker
import sys
import requests
import json
from docker_registry_client import DockerRegistryClient
from requests import HTTPError

def get_tags(client, repositories, config):
    result = set()
    for repository in repositories:
        try:
            tags = client.repository(repository).tags()
        except HTTPError as e:
            if e.response.status_code == 404:
                # sys.stdout.write("repository %s not found" % repository)
                print("repository %s not found" % repository)
                tags = []
            else:
                raise e

        for tag in tags:
            for prefix in config['prefix']:
                if prefix in tag:
                    result.add(repository + ':' + tag)

    return result


def strip_scheme(url):
    parsed_url = urlparse(url)
    scheme = "%s://" % parsed_url.scheme
    return parsed_url.geturl().replace(scheme, '', 1)


# Функция для загрузки config.yml 
def load_config():
    with open('config.yml') as f:
        return yaml.load(f)


def determine_password(config, kind):
    if kind == 'src':
        config_file_key = 'source_registry'
        env_var = 'SOURCE_REGISTRY_PASSWORD'
    elif kind == 'dst':
        config_file_key = 'destination_registry'
        env_var = 'DESTINATION_REGISTRY_PASSWORD'
    else:
        raise Exception("Invalid registry kind:", kind)

    config_file_password = config[config_file_key].get('password')
    if config_file_password is not None:
        return str(config_file_password)

    env_value = os.environ.get(env_var)

    if env_value is not None:
        # sys.stdout.write("Using password from environment variable", env_var)
        print("Using password from environment variable", env_var)
        return env_value

    return None

# Проверка на основную программу
if __name__ == '__main__':

    # Загрузка конфига
    config = load_config()

    # Берем url реестров для синхронизации
    src_registry_url = config['source_registry']['url']


    # Получаем логин и пароль из конфига
    # ----------------------------------
    src_username = None if 'username' not in config['source_registry'] else str(config['source_registry']['username'])
    src_password = determine_password(config, 'src')
    # ----------------------------------

    # Регистрация в реестрах 
    src_client = DockerRegistryClient(src_registry_url, username=src_username, password=src_password)

    # Создаем экземпляр клиента
    docker_client = docker.from_env()

    # Авторизация
    docker_client.login(registry=src_registry_url, username=src_username, password=src_password)
    
    # Берем список контейнеров для синхронизации
    repositories = config['repositories']

    url = src_registry_url + "/v2/_catalog"
    print("URL: "+url)
    r = requests.get(url)

    j = json.dumps(r.json())
    print(j)

    # # Вытаскиваем из реесторов теги, согласно списку из конфига
    # src_tags = get_tags(src_client, repositories, config)
    # dst_tags = get_tags(dst_client, repositories, config)

    # # Выясняем каких тегов нет в dst реестре
    # missing_tags = src_tags - dst_tags

    # # Цикл по недостающим тегам
    # for missing_tag in missing_tags:
    #     # Создаем теги с указателями на реестры
    #     src_tag = strip_scheme(src_registry_url) + '/' + missing_tag
    #     dst_tag = strip_scheme(dst_registry_url) + '/' + missing_tag

    #     # Пулим контейнера из src реестра
    #     # sys.stdout.write("Pulling:", src_tag)
    #     print("Pulling: "+ src_tag)
    #     docker_client.images.pull(src_tag)

    #     # Берем загруженный docker контейнер и меняем ему тег 
    #     # sys.stdout.write("Changing %s to %s" % (src_tag, dst_tag,))
    #     print("Changing %s to %s" % (src_tag, dst_tag,))
    #     src_image = docker_client.images.get(name=src_tag)
    #     src_image.tag(dst_tag)

    #     # Пуш в dst реестр
    #     # sys.stdout.write("Pushing:", dst_tag)
    #     print("Pushing: "+ dst_tag)
    #     docker_client.images.push(dst_tag)
