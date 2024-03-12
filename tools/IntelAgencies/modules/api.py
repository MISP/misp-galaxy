import requests

class WikipediaAPI():
    def __init__(self):
        self.base_url = 'https://en.wikipedia.org/w/api.php'

    def get_page_summary(self, page_title):
        params = {
            'action': 'query',
            'format': 'json',
            'titles': page_title,
            'prop': 'extracts',
            'explaintext': True,
        }
        
        try:
            response = requests.get(self.base_url, params=params)
            data = response.json()
            page_id = next(iter(data['query']['pages']))
            return data['query']['pages'][page_id]['extract']
        except Exception as e:
            print(f'Error: {e}')
            return None
        
    def get_page_content(self, page_title):
        params = {
            'action': 'query',
            'format': 'json',
            'titles': page_title,
            'prop': 'revisions',
            'rvprop': 'content',
        }
        try:
            response = requests.get(self.base_url, params=params)
            data = response.json()
            page_id = next(iter(data['query']['pages']))
            return data['query']['pages'][page_id]['revisions'][0]['*']
        except Exception as e:
            print(f'Error: {e}')
            return None
        
    def get_page_html(self, page_title):
        params = {
            'action': 'parse',
            'format': 'json',
            'page': page_title,
            'prop': 'text',
            'disableeditsection': True, 
        }
        try:
            response = requests.get(self.base_url, params=params)
            data = response.json()
            return data['parse']['text']['*']
        except Exception as e:
            print(f'Error: {e}')
            return None
        
    def get_authors(self, page_title):
        params = {
            'action': 'query',
            'format': 'json',
            'titles': page_title,
            'prop': 'contributors',
        }
        try:
            response = requests.get(self.base_url, params=params)
            data = response.json()
            page_id = next(iter(data['query']['pages']))
            return data['query']['pages'][page_id]['contributors']
        except Exception as e:
            print(f'Error: {e}')
            return None