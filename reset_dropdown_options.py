import argparse
from dotenv import load_dotenv

from core.utils import load_logsheets
from jotform_api.utils import JotformAPI


def main(form_ids):
    load_dotenv('CONFIG.env')
    logsheet_configs = load_logsheets()
    jotform_api = JotformAPI()

    if len(form_ids) == 0:
        form_ids = list(logsheet_configs.keys())
    else:
        form_ids = list(form_ids.split(','))
    
    for form_id in form_ids:
        actions = logsheet_configs[form_id].get('actions', dict())
        questions = actions.get('update_dropdown_options', [])
        for question in questions:
            question_details = jotform_api.get_question_details(question['form_id'], question['question_id'])
            current_list = question_details['content']['list']
            question_name = question_details['content']['text']
            print(f'{logsheet_configs[question['form_id']]['worksheet']} - {question_name}:\n[{current_list.replace('\n', ', ')}] -> .\n')
            jotform_api.update_dropdown_options(question['form_id'], question['question_id'], '.')


if __name__ == '__main__':
    args_parser = argparse.ArgumentParser(description='Reset dropdown option for logsheets')

    args_parser._action_groups.pop()
    optional = args_parser.add_argument_group('optional arguments')
    optional.add_argument('--form_ids', type=str, default='', 
                          help='Specify form IDs, apply to all by default.')
    
    args = args_parser.parse_args()
    main(args.form_ids)
 