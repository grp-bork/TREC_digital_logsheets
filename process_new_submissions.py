from dotenv import load_dotenv
import argparse
import pandas as pd
import datetime
from zoneinfo import ZoneInfo

from jotform_api.utils import JotformAPI
from google_api.utils import GoogleAPI
from core.utils import load_logsheets, load_submission_tracker, update_submission_tracker, update_status
from core.processing import process_submissions
from core.actions import run_actions
from owncloud_api.store_jsons import store_submissions_to_oc


def main():
    load_dotenv('CONFIG.env')

    logsheet_configs = load_logsheets()
    jotform_api = JotformAPI()
    google_api = GoogleAPI()

    submissions = dict()

    now = datetime.datetime.now(ZoneInfo("Europe/Paris"))

    print(f'>>> {now}')

    print('Load submission tracker.')
    submission_tracker = load_submission_tracker(google_api)
    tracker_updated = False

    for form_id in logsheet_configs.keys():
        print(f'Processing form {form_id}...')
        # process submissions
        config = logsheet_configs[form_id]
        
        filter_datetime = submission_tracker.get(form_id, None)
        print('\tObtaining new submissions... ', end='')
        submissions = jotform_api.get_submissions(form_id, filter_datetime=filter_datetime)

        if len(submissions['content']) != 0:
            print(len(submissions['content']))
            # parse submission and extract metadata
            print('\tProcessing submissions...')
            processed_submissions = process_submissions(submissions, config.get('postprocessing', dict()))

            # store war submissions to OwnCloud for backup
            print('\tBacking up submissions to OwnCloud...')
            store_submissions_to_oc(submissions)
            processed_df = pd.DataFrame(processed_submissions)

            # store to Google sheet
            print('\tStoring submissions in Google sheets...')
            row_dicts = processed_df.to_dict(orient="records")
            for row in row_dicts:
                google_api.add_row(config['target_sheet'], config['worksheet'], row)
                if 'backup_sheet' in config:
                    google_api.add_row(config['backup_sheet'], config['worksheet'], row)
                run_actions(row, config.get('actions', dict()), jotform_api)

            # update submission_tracker
            submission_tracker[form_id] = submissions['content'][0]['created_at']
            tracker_updated = True
        else:
            print(0)

    print('<<<')

    submission_tracker = pd.DataFrame(list(submission_tracker.items()), columns=['form_id', 'datetime'])
    if tracker_updated:
        update_submission_tracker(google_api, submission_tracker)

    update_status(logsheet_configs, submission_tracker, tracker_updated, now)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description='Process new logsheet submissions')

    args_parser._action_groups.pop()
    optional = args_parser.add_argument_group('optional arguments')
    
    args = args_parser.parse_args()
    main()
