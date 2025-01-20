""" 
FileHandling.py

Utility functions for handling files.
"""

import os
import requests

def download_file(url: str, params: dict, save_dir: str, filename: str) -> str:
    """
    Downloads a file from a url to the specified location.

    :param url: URL of the file to download.
    :param params: Variable elements of the URL.
    :param save_dir: Directory to save the file to.
    :param filename: Name of the file to save.
    
    :return: Path to the saved file.
    """
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, filename)
    
    # If file already exists, skip download
    if os.path.isfile(save_path):
        return save_path

    # Download the file
    response = requests.get(url, params=params)
    response.raise_for_status()
    
    # Write the content to a file at the specified location
    with open(save_path, 'wb') as file:
        file.write(response.content)
    
    return save_path