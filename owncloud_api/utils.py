import os
import requests
from urllib.parse import unquote, urlparse
from xml.etree import ElementTree


class OwnCloudAPI:
    def __init__(self, subfolder):
        self.username = os.environ["OWNCLOUD_USERNAME"]
        self.password = os.environ["OWNCLOUD_PASSWORD"]
        self.owncloud_url = f"https://oc.embl.de/remote.php/dav/files/matej.trojak%40embl.de/TREC digital logsheets/{subfolder}"

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
    
    def download_txt_file(self, remote_path):
        """Download txt file form remote path

        Args:
            remote_path (str): location of remote file
        """
        response = requests.get(f'{self.owncloud_url}/{remote_path}',
            auth=(self.username, self.password)
        )
        success = response.status_code in [200, 201, 204]
        if not success:
            print({response.status_code} - {response.text})
        else:
            return response.text
    
    def download_json_file(self, remote_path):
        """Download JSON file form remote path

        Args:
            remote_path (str): location of remote file
        """
        response = requests.get(f'{self.owncloud_url}/{remote_path}',
            auth=(self.username, self.password)
        )
        success = response.status_code in [200, 201, 204]
        if not success:
            print({response.status_code} - {response.text})
        else:
            return response.json()
        
    def get_remote_folders(self, remote_path):
        """Inspect remote folder and get all subfolders

        Args:
            remote_path (str): target remote destination

        Returns:
            list: list of subfolders
        """
        headers = {
            "Depth": "1"  # "1" lists contents (not recursive)
        }
        response = requests.request("PROPFIND", f'{self.owncloud_url}/{remote_path}', 
                                    auth=(self.username, self.password), 
                                    headers=headers)
        
        if response.status_code not in (207, 200):
            print(f'{response.status_code} - {response.text}')
        else:
            tree = ElementTree.fromstring(response.content)

            namespace = {"d": "DAV:"}
            files = [
                elem.find("d:href", namespace).text
                for elem in tree.findall("d:response", namespace)
            ]

            return [unquote(urlparse(file_url).path).split('/')[-2] for file_url in files]
        
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
