import os
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials


def create_keyfile_dict():
    """Build dict of Google credentials from env variables

    Returns:
        dict: credentials
    """
    variables_keys = {
        'type': os.environ.get('SHEET_TYPE'),
        'project_id': os.environ.get('SHEET_PROJECT_ID'),
        'private_key_id': os.environ.get('SHEET_PRIVATE_KEY_ID'),
        'private_key': os.environ.get('SHEET_PRIVATE_KEY').replace('\\n', '\n'),
        'client_email': os.environ.get('SHEET_CLIENT_EMAIL'),
        'client_id': os.environ.get('SHEET_CLIENT_ID'),
        'auth_uri': os.environ.get('SHEET_AUTH_URI'),
        'token_uri': os.environ.get('SHEET_TOKEN_URI'),
        'auth_provider_x509_cert_url': os.environ.get('SHEET_AUTH_PROVIDER_X509_CERT_URL'),
        'client_x509_cert_url': os.environ.get('SHEET_CLIENT_X509_CERT_URL'),
        'universe_domain': os.environ.get('UNIVERSE_DOMAIN')
    }
    return variables_keys


class GoogleAPI:
    def __init__(self):
        scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
        creds = ServiceAccountCredentials.from_json_keyfile_dict(create_keyfile_dict(), scope)
        self.client = gspread.authorize(creds)

    def read_table(self, file_key, worksheet):
        """Read remote Google sheet as a Pandas dataframe

        Args:
            file_key (str): identifier of Google sheet
            worksheet (str): identifier of sheet tab

        Returns:
            dataframe: created Pandas dataframe
        """
        spreadsheet = self.client.open_by_key(file_key)
        sheet = spreadsheet.worksheet(worksheet)
        
        data = sheet.get_all_values()
        header = data[0]
        df = pd.DataFrame(data[1:], columns=header)
        return df

    def overwrite_table(self, file_key, worksheet, df):
        """Write table to the Google sheet

        Args:
            file_key (str): identifier of Google sheet
            worksheet (str): identifier of sheet tab
            df (dataframe): target table as dataframe
        """
        spreadsheet = self.client.open_by_key(file_key)
        sheet = spreadsheet.worksheet(worksheet)
        sheet.update([df.columns.values.tolist()] + df.values.tolist())
