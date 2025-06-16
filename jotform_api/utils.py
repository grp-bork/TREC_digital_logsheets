import requests
import json
import urllib.parse


class JotformAPI:
    def __init__(self, base_url, api_key):
        self.base_url = base_url
        self.api_key = api_key

    def get_submissions(self, form_id, filter_datetime=None):
        suffix = ''
        if filter_datetime is not None:
            params = {'filter': json.dumps({'created_at:gt': filter_datetime})}
            suffix = '&' + urllib.parse.urlencode(params)
             
        response = requests.get(f'{self.base_url}/form/{form_id}/submissions?apiKey={self.api_key}{suffix}')
        return json.loads(response.text)
