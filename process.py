from dotenv import load_dotenv
import argparse
import pandas as pd

from jotform_api.utils import JotformAPI
from google_api.utils import GoogleAPI
from core.utils import load_logsheets, merge_tables, load_submission_tracker, update_submission_tracker
from core.processing import process_submissions


def main(process_all):
    load_dotenv('CONFIG.env') # env file for local testing

    logsheet_configs = load_logsheets()
    jotform_api = JotformAPI()
    google_api = GoogleAPI()

    submissions = dict()

    submission_tracker = load_submission_tracker(google_api)

    for form_id in logsheet_configs.keys():
        # process submissions
        config = logsheet_configs[form_id]
        filter_datetime = None
        if not process_all:
            filter_datetime = submission_tracker.get(form_id, None)
        submissions = jotform_api.get_submissions(form_id, filter_datetime=filter_datetime)
        processed_submissions = process_submissions(submissions, config.get('postprocessing', dict()))

        # store to Google sheet
        if processed_submissions:
            processed_df = pd.DataFrame(processed_submissions)
            if not process_all:
                online_table = google_api.read_table(config['target_sheet'], config['worksheet'])
                merged_df = merge_tables(online_table, processed_df)
                google_api.overwrite_table(config['target_sheet'], config['worksheet'], merged_df)
            else:
                processed_df = processed_df.where(pd.notnull(processed_df), None)
                google_api.overwrite_table(config['target_sheet'], config['worksheet'], processed_df)

            # update submission_tracker
            submission_tracker[form_id] = submissions['content'][0]['created_at']

    submission_tracker = pd.DataFrame(list(submission_tracker.items()), columns=['form_id', 'datetime'])
    update_submission_tracker(google_api, submission_tracker)

        # TODO store to OC for backup - only store if filename with submission_id does not exist - how to quickly check?
        # need to compare with what I already had in table before I overwrite it


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description='Process new logsheet submissions')

    args_parser._action_groups.pop()
    optional = args_parser.add_argument_group('optional arguments')
    optional.add_argument('--process_all', action=argparse.BooleanOptionalAction, default=False,
                          help='set if we want to process all submissions again')
    args = args_parser.parse_args()
    main(args.process_all)
