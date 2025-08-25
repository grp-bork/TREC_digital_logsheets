class Curator:
    def split_configurable_list(self, name, values):
        output = dict()
        index = 0
        for items in eval(values):
            index += 1
            for key in items.keys():
                output[f'{key}_{index}'] = items[key]
        return output
    
    def extract_time(self, name, values):
        return {name: values['timeInput']}
    
    def process_other_option(self, name, values):
        if type(values) == dict:
            return {name: values['other']}
        else:
            return {name: values}

    def process_file_upload(self, name, values):
        if len(values) != 0:
            return {name: values[0]}
        return {name: None}

    def process_site_layout(self, name, values):
        output = dict()
        lst_values = eval(values['Distance (m)'])
        for i, key in enumerate('ABCDEFGH'):
            if lst_values[i] != '':
                output[f'distance {key} (m)'] = int(lst_values[i])
        return output

    def process_multiple_choice(self, name, values):
        return {name: ','.join(values)}


def process_submissions(submissions, postprocessing):
    """Process new submissions for a form

    Args:
        submissions (list): list of dicts containing submissions
        postprocessing (dict): specification of attributes with special treatment

    Returns:
        list: processed submissions
    """
    curator = Curator()

    results = []

    for submission in submissions['content']:
        result = {'Submission ID': submission['id'],
                  'Submission date': submission['created_at']}
        for question in submission['answers'].values():
            if question['type'] not in ['control_button', 'control_head', 'control_image', 'control_divider']:
                if question['text'] in postprocessing:
                    if question.get('answer'):
                        conf_result = getattr(curator, postprocessing[question['text']])(question['text'], 
                                                                                         question['answer'])
                        result = result | conf_result
                else:
                    result[question['text']] = question.get('answer', None)

        results.append(result)

    return results
