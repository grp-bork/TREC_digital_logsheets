from dotenv import load_dotenv
import argparse
import pandas as pd

from google_api.utils import GoogleAPI
from jotform_api.utils import JotformAPI
from core.utils import load_logsheets
from core.processing import process_submissions
from owncloud_api.store_jsons import load_oc_jsons


def main(source, use_local_headers):
    load_dotenv('CONFIG.env') # env file for local testing

    logsheet_configs = load_logsheets()
    jotform_api = JotformAPI()
    google_api = GoogleAPI()

    with pd.ExcelWriter('all_submissions.xlsx', engine='openpyxl') as writer:
        for form_id in logsheet_configs.keys():
            print(f'Processing form {form_id}...')
            config = logsheet_configs[form_id]
            if source == 'jotform':
                submissions = jotform_api.get_submissions(form_id)
            else:
                submissions = load_oc_jsons(form_id)

            if len(submissions['content']) != 0:
                print(len(submissions['content']))
                processed_submissions = process_submissions(submissions, config.get('postprocessing', dict()))
                processed_df = pd.DataFrame(processed_submissions)

                # reorder DataFrame
                if not use_local_headers:
                    header = google_api.get_header(config['backup_sheet'], config['worksheet'])

                    for col in header:
                        if col not in processed_df.columns:
                            processed_df[col] = None

                    remaining = [col for col in processed_df.columns if col not in header]
                    processed_df = processed_df[header + remaining]

                    processed_df = processed_df.sort_values(by='Submission date')
                
                processed_df.to_excel(writer, sheet_name=config['worksheet'], index=False)
            else:
                print(0)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description='Process new logsheet submissions')

    args_parser._action_groups.pop()
    optional = args_parser.add_argument_group('optional arguments')
    optional.add_argument('--source', type=str, default='jotform', 
                          help='Specify source for submissions, can be jotform or oc.')
    optional.add_argument('--use_local_headers', action=argparse.BooleanOptionalAction, default=False)
    
    args = args_parser.parse_args()
    main(args.source, args.use_local_headers)
