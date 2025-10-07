import os
import pandas as pd
import gspread
from oauth2client.service_account import ServiceAccountCredentials

from core.utils import clean_up_nulls
from google_api.throttling import rate_limited_with_retry


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

    @rate_limited_with_retry()
    def access_sheet(self, file_key, worksheet):
        """Access remote Google worksheet

        Args:
            file_key (str): identifier of Google sheet
            worksheet (str): identifier of sheet tab

        Returns:
            sheet: Google sheet
        """
        spreadsheet = self.client.open_by_key(file_key)
        return spreadsheet.worksheet(worksheet)

    @rate_limited_with_retry()
    def read_table(self, file_key, worksheet):
        """Read remote Google sheet as a Pandas dataframe

        Args:
            file_key (str): identifier of Google sheet
            worksheet (str): identifier of sheet tab

        Returns:
            dataframe: created Pandas dataframe
        """
        sheet = self.access_sheet(file_key, worksheet)
        data = sheet.get_all_values()
        header = data[0]
        df = pd.DataFrame(data[1:], columns=header)
        return df
    
    @rate_limited_with_retry()
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

    @rate_limited_with_retry()
    def add_rows(self, file_key, worksheet, row_dicts):
        """Add a list of rows to the Google sheet

        Also resolve any changes in the headers

        Args:
            file_key (str): identifier of Google sheet
            worksheet (str): identifier of sheet tab
            row_dicts (list): list of dict representation of logsheet contents
        """
        sheet = self.access_sheet(file_key, worksheet)
        # Get current header
        header = sheet.row_values(1)

        # Detect and add missing columns
        missing_cols = [key for key in row_dicts[0] if key not in header]
        if missing_cols:
            updated_header = header + missing_cols
            sheet.update('1:1', [updated_header])
            header = updated_header

        # Prepare row values in correct order
        values_to_append = []
        for row in row_dicts:
            row_values = [row.get(col, "") for col in header]
            values_to_append.append(clean_up_nulls(row_values))

        # Append rows
        sheet.append_rows(values_to_append)

    @rate_limited_with_retry()
    def get_header(self, file_key, worksheet):
        sheet = self.access_sheet(file_key, worksheet)
        return sheet.row_values(1)

    @rate_limited_with_retry()
    def is_checkbox_checked(self, file_key, worksheet, cell='A1'):
        """Check if a checkbox in the specified cell is checked
        
        Args:
            file_key (str): identifier of Google sheet
            worksheet (str): identifier of sheet tab
            cell (str): cell reference (default: 'A1')
            
        Returns:
            bool: True if checkbox is checked, False otherwise
        """
        sheet = self.access_sheet(file_key, worksheet)
        try:
            cell_value = sheet.acell(cell).value
            # Google Sheets checkboxes return "TRUE" or "FALSE" as strings
            return cell_value == "TRUE"
        except Exception as e:
            print(f"Error checking checkbox in {cell}: {e}")
            return False

    @rate_limited_with_retry()
    def set_checkbox(self, file_key, worksheet, cell='A1', checked=False):
        """Set a checkbox in the specified cell
        
        Args:
            file_key (str): identifier of Google sheet
            worksheet (str): identifier of sheet tab
            cell (str): cell reference (default: 'A1')
            checked (bool): whether to check or uncheck the checkbox
        """
        sheet = self.access_sheet(file_key, worksheet)
        value = True if checked else False
        sheet.update(cell, [[value]])

    @rate_limited_with_retry()
    def get_all_worksheets(self, file_key):
        """Get all worksheet names from a spreadsheet
        
        Args:
            file_key (str): identifier of Google sheet
            
        Returns:
            list: list of worksheet names
        """
        try:
            spreadsheet = self.client.open_by_key(file_key)
            return [ws.title for ws in spreadsheet.worksheets()]
        except Exception as e:
            print(f"Error getting worksheets: {e}")
            return []

    @rate_limited_with_retry()
    def clear_worksheet_data(self, file_key, worksheet):
        """Clear all data from a worksheet
        
        Args:
            file_key (str): identifier of Google sheet
            worksheet (str): identifier of sheet tab
        """
        sheet = self.access_sheet(file_key, worksheet)
        header = sheet.row_values(1)
        sheet.clear()
        sheet.update('1:1', [header])
        sheet.freeze(rows=1)
