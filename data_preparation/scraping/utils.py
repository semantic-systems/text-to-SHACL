"""
 utils.py

 Master's Thesis
 Seike Appold
 
 Utility functions for preparing the data.
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlsplit


def remove_html_tags(text) -> str:
    """Remove HTML tags from a string."""
    soup = BeautifulSoup(text, "html.parser")
    return soup.text.strip()


def download_file(url: str, params: dict, save_dir: str, filename: str) -> str:
    """Download a file from a url to the specified location.

    :param url: URL of the file to download.
    :param params: Variable elements of the URL, if any.
    :param save_dir: Directory to save the file to.
    :param filename: Name of the file to save.
    :return: Path to the saved file.
    """
    # Ensure the save directory exists
    os.makedirs(save_dir, exist_ok=True)

    # If file already exists, skip download
    save_path = os.path.join(save_dir, filename)
    if os.path.isfile(save_path):
        print(f"File already exists at {save_path}. Skipping download.")
        return save_path

    # Download the file and save it to the specified location
    try:
        response = requests.get(url, params=params)
        response.raise_for_status()
        with open(save_path, 'wb') as file:
            file.write(response.content)
        print(f"File successfully downloaded and saved to {save_path}.")
        return save_path
    except requests.RequestException as e:
        print(f"Failed to download {filename}: {e}")
        return None


def get_filename_from_url(url: str) -> str:
    """Extract the filename from a URL."""
    basename = os.path.basename(urlsplit(url).path)
    if not basename:
        raise ValueError("Filename could not be extracted from URL.")
    return basename