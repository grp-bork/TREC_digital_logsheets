import requests
import json


class JotformAPI:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def get_submissions(self, form_id):
        response = requests.get(f'{self.base_url}/form/{form_id}/submissions?apiKey={self.api_key}')
        return json.loads(response.text)
