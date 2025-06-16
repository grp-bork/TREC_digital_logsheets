from dotenv import load_dotenv
import os
import json

from jotform_api.utils import JotformAPI
from google_api.utils import GoogleAPI
from core.processing import load_latest_submissions


def main():
    with open(f'logsheet_configs/{os.environ["LOGSHEETS_FILE"]}') as json_data:
        logsheet_configs = json.load(json_data)

    jotform_api = JotformAPI()
    google_api = GoogleAPI()

    submissions = dict()

    latest_submissions = load_latest_submissions(google_api)

    for form_id in logsheet_configs.keys():
        filter_datetime = latest_submissions.get(form_id, None)
        submissions[form_id] = jotform_api.get_submissions(form_id, filter_datetime=filter_datetime)

    print(submissions)


if __name__ == '__main__':
    # env file for local testing
    load_dotenv('CONFIG.env', verbose=True)
    main()
