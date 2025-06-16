import os
import requests
import json
import urllib.parse


class JotformAPI:
    def __init__(self):
        self.base_url = os.environ["JOTFORM_URL"]
        self.api_key = os.environ["JOTFORM_API_KEY"]

    def get_submissions(self, form_id, filter_datetime=None):
        """Get existing submissions using Jotform API

        Args:
            form_id (str): identifier of a form
            filter_datetime (str, optional): Datetime of the last known submission. Defaults to None, format "2025-06-15 08:28:53"

        Returns:
            _type_: dict of all submissions
        """
        suffix = ''
        if filter_datetime is not None:
            params = {'filter': json.dumps({'created_at:gt': filter_datetime})}
            suffix = '&' + urllib.parse.urlencode(params)
             
        response = requests.get(f'{self.base_url}/form/{form_id}/submissions?apiKey={self.api_key}{suffix}')
        return json.loads(response.text)
