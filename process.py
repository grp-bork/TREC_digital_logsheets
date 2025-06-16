from dotenv import load_dotenv
import os
import json

from jotform_api.utils import JotformAPI


def main():
    with open(f'logsheet_configs/{os.environ["LOGSHEETS_FILE"]}') as json_data:
        logsheet_configs = json.load(json_data)

    jotform_api = JotformAPI(os.environ["JOTFORM_URL"], os.environ["JOTFORM_API_KEY"])

    submissions = dict()

    for form_id in logsheet_configs.keys():
        submissions[form_id] = jotform_api.get_submissions(form_id)

    print(submissions)


if __name__ == '__main__':
    # env file for local testing
    load_dotenv('CONFIG.env')
    main()
