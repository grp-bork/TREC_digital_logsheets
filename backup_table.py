import requests
import datetime
import hashlib
import os
from dotenv import load_dotenv

from owncloud_api.utils import OwnCloudAPI


def compute_md5(file_path):
    hasher = hashlib.md5()
    with open(file_path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b''):
            hasher.update(chunk)
    return hasher.hexdigest()


load_dotenv('CONFIG.env')

EXCEL_FILE = 'spreadsheet.xlsx'
HASH_FILE = 'last_backup_hash.txt'
GOOGLE_SHEET_ID = os.getenv('GOOGLE_SHEET_ID')

# download Google spreadsheet as Excel
print('Download Excel spreadsheet')
url = f'https://docs.google.com/spreadsheets/d/{GOOGLE_SHEET_ID}/export?format=xlsx'
response = requests.get(url)
response.raise_for_status()

with open(EXCEL_FILE, 'wb') as f:
    f.write(response.content)

# compute MD5 of the Excel file
print('Compute its MD5 hash')
current_hash = compute_md5(EXCEL_FILE)

# get MD5 of the last file
print('Download previous M5D hash')
owncloud_api = OwnCloudAPI('google_backups')
previous_hash = owncloud_api.download_txt_file(HASH_FILE)

# compare with stored hash
if current_hash == previous_hash:
    print('No changes detected. Skipping upload.')
    exit(0)

# create filename from current date
now = datetime.datetime.now().strftime('%Y%m%d')
output_filename = f'{now}.xlsx'

# upload to OwnCloud
with open(EXCEL_FILE, 'rb') as file:
    owncloud_api.upload_file(f'files/{output_filename}', file)
    print(f'Uploaded {output_filename} to OwnCloud.')

# save new hash
with open(HASH_FILE, 'w') as file:
    file.write(current_hash)

# store new hash
with open(HASH_FILE, 'rb') as file:
    owncloud_api.upload_file(HASH_FILE, file)
    print(f'Uploaded {HASH_FILE} to OwnCloud.')
