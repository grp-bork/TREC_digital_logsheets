from io import BytesIO
import json

from owncloud_api.utils import OwnCloudAPI


def store_submissions_to_oc(submissions):
    owncloud_api = OwnCloudAPI()

    for submission in submissions['content']:
        # create existing folder for form
        folder = submission['form_id']
        owncloud_api.check_create_folder(folder)

        # create existing folder for submission
        submission_id = submission['id']
        owncloud_api.check_create_folder(submission_id, folder)
        
        json_bytes = json.dumps(submission, ensure_ascii=False, indent=2).encode('utf-8')
        json_bytes = BytesIO(json_bytes)
        owncloud_api.upload_file(f'{folder}/{submission_id}/content.json', json_bytes)
