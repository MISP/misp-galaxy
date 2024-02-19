import requests

class TidalAPI:
    def __init__(self):
        self.base_url = 'https://app-api.tidalcyber.com/api/v1/'

    def get_data(self, endpoint):
        url = self.base_url + endpoint
        try:
            response = requests.get(url)
            return response.json()
        except Exception as e:
            print(f'Error: {e}')
            return None

