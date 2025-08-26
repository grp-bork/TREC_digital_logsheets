import requests
import datetime
import os
from dotenv import load_dotenv
from oauth2client.service_account import ServiceAccountCredentials
from googleapiclient.discovery import build

from owncloud_api.utils import OwnCloudAPI
from google_api.utils import create_keyfile_dict


load_dotenv('CONFIG.env')

EXCEL_FILE = 'spreadsheet.xlsx'
LAST_FILE = 'last_backup.txt'

for sheet_type in ['LSI', 'AML']:
    print(f'>> Backing up {sheet_type} spreadsheet.')
    GOOGLE_SHEET_ID = os.getenv(f'{sheet_type}_GOOGLE_SHEET_ID')

    scope = ['https://www.googleapis.com/auth/drive.metadata.readonly']
    creds = ServiceAccountCredentials.from_json_keyfile_dict(create_keyfile_dict(), scope)
    service = build('drive', 'v3', credentials=creds)

    # get modified timestamp
    result = service.files().get(fileId=GOOGLE_SHEET_ID, fields='modifiedTime').execute()
    last_modified = datetime.datetime.strptime(result['modifiedTime'], '%Y-%m-%dT%H:%M:%S.%fZ')

    # get the last backup timestamp
    print('Download file with last backup timestamp.')
    owncloud_api = OwnCloudAPI(f'google_backups/{sheet_type}')
    last_backup = owncloud_api.download_txt_file(LAST_FILE)
    last_backup = datetime.datetime.strptime(last_backup, '%Y-%m-%dT%H:%M:%S.%fZ')

    # compare with last backup timestmap
    if last_modified <= last_backup:
        print('No changes detected. Skipping upload.')
        exit(0)

    # download Google spreadsheet as Excel
    print('Download Excel spreadsheet')
    url = f'https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?format=xlsx'
    response = requests.get(url)
    response.raise_for_status()

    with open(EXCEL_FILE, 'wb') as f:
        f.write(response.content)

    # create filename from current date
    now = datetime.datetime.now().strftime('%Y%m%d')
    output_filename = f'{now}.xlsx'

    # upload to OwnCloud
    with open(EXCEL_FILE, 'rb') as file:
        owncloud_api.upload_file(f'files/{output_filename}', file)
        print(f'Uploaded {output_filename} to OwnCloud.')

    # save new timestamp
    with open(LAST_FILE, 'w') as file:
        file.write(result['modifiedTime'])

    # store new timestamp
    with open(LAST_FILE, 'rb') as file:
        owncloud_api.upload_file(LAST_FILE, file)
        print(f'Uploaded {LAST_FILE} to OwnCloud.')
