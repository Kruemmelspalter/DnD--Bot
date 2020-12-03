import urllib

import requests


class DnD5eApi:
    def __init__(self):
        self.API_URL = 'https://www.dnd5eapi.co'
        if not self.ping():
            raise ConnectionError()

    def ping(self):
        return requests.head(self.API_URL).status_code == 200

    async def get_item(self, name):
        response = requests.get(self.API_URL + '/api/equipment?name=' + urllib.parse.quote(name)).json()
        if response['count'] == 0:
            return []

        elif response['count'] == 1:
            return response['results'][0]

        elif response['count'] >= 2:
            return response['results']
