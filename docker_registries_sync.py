# -*- coding: utf-8 -*-
try:
    from urllib.parse import urlparse
except ImportError:
    from urlparse import urlparse

import os
import yaml
import docker
import sys
import json
import requests
import datetime
from docker_registry_client import DockerRegistryClient
from docker_registry_client import Repository
from requests import HTTPError

def get_tags(client, repositories, config):
    result = set()
    for repository in repositories:
        try:
            tags = client.repository(repository).tags()
        except HTTPError as e:
            if e.response.status_code == 404:
                # print(log("repository %s not found" % repository))
                tags = []
            else:
                raise e
        if config['prefixes']:
            for tag in tags:
                for prefix in config['prefix']:
                    if prefix in tag:
                        result.add(repository + ':' + tag)
        else: 
            for tag in tags:
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
        print(log("Using password from environment variable", env_var))
        return env_value

    return None

def log(text):
    now = datetime.datetime.now()
    time = str(now.strftime("%d-%m-%y %H:%M - "))
    return time+text

if __name__ == '__main__':
    print(log("Start synchronization"))

    # Загрузка конфига
    config = load_config()

    # Берем url реестров для синхронизации
    src_registry_url = config['source_registry']['url']
    dst_registry_url = config['destination_registry']['url']


    # Получаем логин и пароль из конфига
    # ----------------------------------
    src_username = None if 'username' not in config['source_registry'] else str(config['source_registry']['username'])
    src_password = determine_password(config, 'src')

    dst_username = None if 'username' not in config['destination_registry'] else str(config['destination_registry']['username'])
    dst_password = determine_password(config, 'dst')
    # ----------------------------------

    # Регистрация в реестрах 
    src_client = DockerRegistryClient(src_registry_url, username=src_username, password=src_password)
    dst_client = DockerRegistryClient(dst_registry_url, username=dst_username, password=dst_password)
    
    # Создаем экземпляр клиента
    docker_client = docker.from_env()

    # Авторизация
    docker_client.login(registry=src_registry_url, username=src_username, password=src_password)
    docker_client.login(registry=dst_registry_url, username=dst_username,password=dst_password)

    # Если включена синхронизация всех репозиториев
    if config['take_all_repositories']:
        # Получаем список репозиториев
        # ----------------------------------
        src_list_repo = requests.get(src_registry_url + "/v2/_catalog").json()
        dst_list_repo = requests.get(dst_registry_url + "/v2/_catalog").json()
        # ----------------------------------
        
        # Получаем теги по списку
        src_tags = get_tags(src_client, src_list_repo['repositories'], config)
        dst_tags = get_tags(dst_client, dst_list_repo['repositories'], config)
    else:
        # Берем список контейнеров для синхронизации
        repositories = config['repositories']
        # Вытаскиваем из реесторов теги, согласно списку из конфига
        src_tags = get_tags(src_client, repositories, config)
        dst_tags = get_tags(dst_client, repositories, config)
    
    print(log(time+"List src_tags: "+str(src_tags)))
    print(log(time+"List dst_tags: "+str(dst_tags)))

    if config['delete_repositories']:
        print('______Delete_repositories______')

        # Выясняем каких тегов нет в dst реестре
        missing_tags = src_tags - dst_tags

        # Выясняем какие теги были удалены в src реестре
        missing_rm_tags = dst_tags - src_tags
        print(log('Missing tags in dst: '+str(missing_tags)))
        print(log('Deleted tags in src: '+str(missing_rm_tags)))

        for missing_rm_tag in missing_rm_tags:
            print(log('Delete: '+str(missing_rm_tag)))

            repo, sep, tag = missing_rm_tag.partition(':')
            headers = {'Accept': 'application/vnd.docker.distribution.manifest.v2+json'}

            print(log('Request: '+dst_registry_url+'/v2/'+repo+'/manifests/'+tag))

            r = requests.get(dst_registry_url+'/v2/'+repo+'/manifests/'+tag, headers=headers)
            r = requests.delete(dst_registry_url+'/v2/'+repo+'/manifests/'+r.headers['Docker-Content-Digest'], headers=headers)
            print(log(r))

    else:
        # Выясняем каких тегов нет в dst реестре
        missing_tags = src_tags - dst_tags

        # Цикл по недостающим тегам
        for missing_tag in missing_tags:
            # Создаем теги с указателями на реестры
            src_tag = strip_scheme(src_registry_url) + '/' + missing_tag
            dst_tag = strip_scheme(dst_registry_url) + '/' + missing_tag

            # Пулим контейнера из src реестра
            print(log("Pulling: "+ src_tag))
            docker_client.images.pull(src_tag)

            # Берем загруженный docker контейнер и меняем ему тег 
            print(log("Changing %s to %s" % (src_tag, dst_tag,)))
            src_image = docker_client.images.get(name=src_tag)
            src_image.tag(dst_tag)

            # Пуш в dst реестр
            print(log("Pushing: "+ dst_tag))
            docker_client.images.push(dst_tag)
