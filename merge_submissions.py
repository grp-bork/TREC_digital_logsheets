import os
from dotenv import load_dotenv

from google_api.utils import GoogleAPI


def merge_submissions():
    """Main function to merge submissions based on checkbox status"""

    load_dotenv('CONFIG.env')
    
    main_source_sheet_id = os.environ.get('MAIN_SHEET_ID_SOURCE')
    main_target_sheet_id = os.environ.get('MAIN_SHEET_ID_TARGET')
    backup_source_sheet_id = os.environ.get('BACKUP_SHEET_ID_SOURCE')
    backup_target_sheet_id = os.environ.get('BACKUP_SHEET_ID_TARGET')
    
    google_api = GoogleAPI()
    
    if google_api.is_checkbox_checked(main_source_sheet_id, "Review"):
        print("Checkbox is checked! Starting merge process...")
    
        # Get all worksheet names from source spreadsheet
        source_worksheets = google_api.get_all_worksheets(main_source_sheet_id)
        # Process each worksheet (except Review)
        for worksheet_name in source_worksheets:
            if worksheet_name != "Review":
                print(f"Processing worksheet: {worksheet_name}")
                # Read data from source worksheet
                source_data = google_api.read_table(main_source_sheet_id, worksheet_name)
                
                if not source_data.empty:
                    print(f"-> Found {len(source_data)} rows of data")

                    print(f"-> Appending data to target spreadsheet.")
                    row_dicts = source_data.to_dict(orient="records")
                    google_api.add_rows(main_target_sheet_id, worksheet_name, row_dicts)
                    google_api.add_rows(backup_target_sheet_id, worksheet_name, row_dicts)

                    # Clear data from source worksheet (keeping headers)
                    print(f"-> Clearing data from source worksheet.")
                    google_api.clear_worksheet_data(main_source_sheet_id, worksheet_name)
                    google_api.clear_worksheet_data(backup_source_sheet_id, worksheet_name)
                    
                    print(f"-> Successfully processed worksheet.")
                else:
                    print(f"-> Empty, skipping...")
                    
        # Reset the checkbox to unchecked
        print("Resetting checkbox to unchecked...")
        google_api.set_checkbox(main_source_sheet_id, "Review", checked=False)
        
        print("Merge process completed successfully!")
    else:
        print("Checkbox is not checked. No action needed.")

if __name__ == "__main__":
    merge_submissions()
