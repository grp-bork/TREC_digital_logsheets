import os
import json
import pandas as pd
import math


def load_logsheets():
    with open(f'logsheet_configs/logsheets.json') as json_data:
        logsheet_configs = json.load(json_data)
        testing_env = (os.environ.get('TESTING', 'False') == 'True')
        if testing_env:
            return {key: val for key, val in logsheet_configs.items() if val.get('testing') is True}
        return logsheet_configs


def load_submission_tracker(google_api):
    df = google_api.read_table(os.environ['SUBMISSION_TRACKER_FILE_KEY'], 'latest')
    return dict(zip(df['form_id'], df['datetime']))


def update_submission_tracker(google_api, submission_tracker):
    google_api.overwrite_table(os.environ['SUBMISSION_TRACKER_FILE_KEY'], 'latest', submission_tracker)


def merge_tables(df1, df2):
    merged = pd.concat([df1, df2], ignore_index=True)
    # convert NaN to None
    return merged.where(pd.notnull(merged), None)


def clean_up_nulls(values):
    return ["" if x is None or x == "nan" or (isinstance(x, float) and math.isnan(x)) else x for x in values]


def update_status(logsheet_configs, submission_tracker, tracker_updated, now):
    # Write latest run timestamp
    last_run_filename = 'last_run.txt'
    with open(last_run_filename, 'w') as f:
        f.write(now.replace(microsecond=0).isoformat())

    if tracker_updated:
        latest_filename = 'lastest_submissions.csv'

        replace_map = {form_id: logsheet_configs[form_id]['worksheet'] for form_id in logsheet_configs.keys()}
        submission_tracker['form_id'] = submission_tracker['form_id'].replace(replace_map)

        submission_tracker.columns = ['Logsheet name', 'Latest submission']
        submission_tracker.to_csv(latest_filename, index=False)
