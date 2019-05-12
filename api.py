import urllib.request
import json

BASE_API_URL = 'https://codeforces.com/api/'


def fetch_submissions(handle):
    url = BASE_API_URL + 'user.status?lang=ru&handle={}&from=1&count=1000'.format(handle)
    connected = False
    while not connected:
        try:
            request = urllib.request.Request(url)
            response = urllib.request.urlopen(request)
            content = response.read()
            connected = True
        except OSError as err:
            print("OS Error: {}".format(err))
            connected = False

    if not connected:
        print("Failed to connect")
        return None

    data = json.loads(content)

    if data['status'] != 'OK':
        print("Failed to query submissions")
        return None

    return data['result']
