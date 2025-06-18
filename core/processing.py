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
        result = dict()
        for question in submission['answers'].values():
            if question['name'] not in ['heading', 'submit2', 'divider']:
                if question['text'] in postprocessing:
                    if question.get('answer'):
                        conf_result = getattr(curator, postprocessing[question['text']])(question['text'], 
                                                                                         question['answer'])
                        result = result | conf_result
                else:
                    result[question['text']] = question.get('answer', None)

        results.append(result)

    return results
