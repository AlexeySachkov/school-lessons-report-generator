import json
import os

BASE_PATH = 'cache/'


def exists(key):
    return os.path.isfile(BASE_PATH + key + '.json')


def save(key, obj):
    with open(BASE_PATH + key + '.json', 'w') as file:
        file.write(json.dumps(obj))


def get(key):
    try:
        with open(BASE_PATH + key + '.json', 'r') as file:
            return json.load(file)
    except FileNotFoundError:
        return None
