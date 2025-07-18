def run_actions(submission, actions, jotform_api):
    """Iterate over defined actions for a form and execute them on the submission

    Args:
        submission (dict): processed submission
        actions (dict): config containing actions to be executed
        jotform_api (JotformAPI): given instance of JotForm API
    """
    for action in actions.keys():
        if action == 'update_dropdown_options':
            for item in actions[action]:
                question_details = jotform_api.get_question_details(item['form_id'], item['question_id'])
                current_list = question_details['content']['list']
                updated_list = current_list + '\n' + submission[item['attribute']]
                jotform_api.update_dropdown_options(item['form_id'], item['question_id'], updated_list)
