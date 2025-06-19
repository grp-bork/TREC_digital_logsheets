from io import BytesIO
import json
import requests

from owncloud_api.utils import OwnCloudAPI


def find_png_strings(data, found=None):
    """Recursively find all PNG links for backup

    Args:
        data (dict): raw submission
        found (list, optional): already found images. Defaults to None.

    Returns:
        list: list of found images
    """
    if found is None:
        found = []

    if isinstance(data, dict):
        for value in data.values():
            find_png_strings(value, found)
    elif isinstance(data, list):
        for item in data:
            find_png_strings(item, found)
    elif isinstance(data, str) and data.lower().endswith('.png'):
        found.append(data)

    return found


def store_submissions_to_oc(submissions):
    """Backup raw submissions to OwnCloud as JSON

    Additionally, download all images created during submission

    Args:
        submissions (dict): obtained submissions
    """
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

        img_filenames = find_png_strings(submission)
        for img_file in img_filenames:
            img_data = requests.get(img_file).content
            filename = img_file.split('/')[-1]
            owncloud_api.upload_file(f'{folder}/{submission_id}/{filename}', img_data)
