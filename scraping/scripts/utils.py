"""
 utils.py

 Master's Thesis
 Seike Appold
 
 - Utility functions for the scraping scripts.
"""

import os
import requests
from bs4 import BeautifulSoup 
from pathlib import Path

def remove_html_tags(text):
    soup = BeautifulSoup(text, "html.parser")
    return soup.text.strip()

def save_path_exists(save_dir: str, filepath: str, activity="download") -> bool:
    # Create the directory if it doesn't exist
    Path(save_dir).mkdir(parents=True, exist_ok=True)

    if os.path.isfile(filepath):
        print(f"File already exists at {filepath}. Skipping {activity}.")
        return True
    return False

def download_file(url: str, params: dict, save_dir: str, filename: str) -> str:
    save_path = os.path.join(save_dir, filename)

    # If file already exists, skip download
    if save_path_exists(save_dir, save_path):
        return save_path

    # If file already exists, skip download
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
        print(f"Failed to download file: {e}")
        return None