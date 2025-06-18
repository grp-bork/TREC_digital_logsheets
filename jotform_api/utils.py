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
            dict: dict of all submissions
        """
        suffix = ''
        if filter_datetime is not None:
            params = {'filter': json.dumps({'created_at:gt': filter_datetime}),
                      'orderby': 'created_at'}
            suffix = '&' + urllib.parse.urlencode(params)
             
        response = requests.get(f'{self.base_url}/form/{form_id}/submissions?apiKey={self.api_key}{suffix}')
        return json.loads(response.text)
    
    def get_form_questions(self, form_id):
        """Get list of form questions

        Args:
            form_id (str): identifier of a form

        Returns:
            dict: response containing questions
        """
        response = requests.get(f'{self.base_url}/form/{form_id}/questions?apiKey={self.api_key}')
        return json.loads(response.text)
    
    def get_question_details(self, form_id, question_id):
        """Get details about a single question

        Args:
            form_id (str): identifier of a form
            question_id (str): identifier of a question

        Returns:
            dict: response containing details
        """
        response = requests.get(f'{self.base_url}/form/{form_id}/question/{question_id}?apiKey={self.api_key}')
        return json.loads(response.text)

    def update_dropdown_options(self, form_id, question_id, values):
        """Update options for a dropdown question

        Args:
            form_id (str): identifier of a form
            question_id (str): identifier of a form
            values (str): newline separated values

        Returns:
            bool: True if request was successful
        """
        headers = {
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        params = {
            'apiKey': self.api_key,
        }

        response = requests.post(f'{self.base_url}/form/{form_id}/question/{question_id}',
                                 params=params,
                                 headers=headers,
                                 data=f'question[list]={values}')
        return response.status_code == 200
