import os


def load_latest_submissions(google_api):
    df = google_api.read_table(os.environ['LATEST_SUBS_FILE_KEY'], 'latest')
    return dict(zip(df['form_id'], df['datetime']))
