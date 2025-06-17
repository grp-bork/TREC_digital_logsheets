import os
import json
import pandas as pd


def load_logsheets():
    with open(f'logsheet_configs/logsheets.json') as json_data:
        logsheet_configs = json.load(json_data)
        testing_env = (os.environ.get('TESTING', 'False') == 'True')
        if testing_env:
            return {key: val for key, val in logsheet_configs.items() if val.get('testing') is True}
        return logsheet_configs


def load_latest_submissions(google_api):
    df = google_api.read_table(os.environ['LATEST_SUBS_FILE_KEY'], 'latest')
    return dict(zip(df['form_id'], df['datetime']))


def update_latest_submissions(google_api, latest_submissions):
    google_api.overwrite_table(os.environ['LATEST_SUBS_FILE_KEY'], 'latest', latest_submissions)


def merge_tables(df1, df2):
    merged = pd.concat([df1, df2], ignore_index=True)
    # convert NaN to None
    return merged.where(pd.notnull(merged), None)
