from dotenv import load_dotenv
import argparse
import pandas as pd

from jotform_api.utils import JotformAPI
from core.utils import load_logsheets
from core.processing import process_submissions


def main():
    load_dotenv('CONFIG.env') # env file for local testing

    logsheet_configs = load_logsheets()
    jotform_api = JotformAPI()

    submissions = dict()

    with pd.ExcelWriter('all_submissions.xlsx', engine='openpyxl') as writer:

        for form_id in logsheet_configs.keys():
            print(f'Processing form {form_id}...')
            config = logsheet_configs[form_id]
            submissions = jotform_api.get_submissions(form_id)

            if len(submissions['content']) != 0:
                print(len(submissions['content']))
                processed_submissions = process_submissions(submissions, config.get('postprocessing', dict()))
                processed_df = pd.DataFrame(processed_submissions)
                processed_df.to_excel(writer, sheet_name=config['worksheet'], index=False)
            else:
                print(0)


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description='Process new logsheet submissions')

    args_parser._action_groups.pop()
    optional = args_parser.add_argument_group('optional arguments')
    
    args = args_parser.parse_args()
    main()
