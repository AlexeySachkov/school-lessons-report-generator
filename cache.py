import json

BASE_PATH = 'cache/'


def save(key, obj):
    with open(BASE_PATH + key + '.json', 'w') as file:
        file.write(json.dumps(obj))


def get(key):
    with open(BASE_PATH + key + '.json', 'r') as file:
        return json.load(file)
