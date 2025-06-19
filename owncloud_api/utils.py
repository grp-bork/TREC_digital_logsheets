import os
import requests


class OwnCloudAPI:
    def __init__(self):
        self.username = os.environ["OWNCLOUD_USERNAME"]
        self.password = os.environ["OWNCLOUD_PASSWORD"]
        self.owncloud_url = "https://oc.embl.de/remote.php/dav/files/matej.trojak%40embl.de/TREC digital logsheets"

    def upload_file(self, remote_path, bytes):
        """Upload a local file to the OwnCloud destination

        Args:
            remote_path (str): destination path within OwnCloud

        Returns:
            bool: True if successful
        """
        response = requests.put(f'{self.owncloud_url}/{remote_path}',
            data=bytes,
            auth=(self.username, self.password)
        )
        success = response.status_code in [200, 201, 204]
        if not success:
            print({response.status_code} - {response.text})
        return success

    def check_create_folder(self, folder_name, remote_path=''):
        """Create new folder in OwnCloud

        Response code 405 is acceptable (folder already exists)

        Args:
            folder_name (str): name of the folder to be created
            remote_path (str, optional): destination path within OwnCloud. Defaults to ''.

        Returns:
            bool: True if successful
        """
        if remote_path:
            folder_name = f'{remote_path}/{folder_name}'

        # Create folder using MKCOL request
        response = requests.request("MKCOL",
                                    f'{self.owncloud_url}/{folder_name}', 
                                    auth=(self.username, self.password)
                                    )
        
        success = response.status_code in [201, 405]
        if not success:
            print({response.status_code} - {response.text})
        return success
