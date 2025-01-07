"""
 utils.py

 Master's Thesis
 Seike Appold
 
 Utility functions for preparing the data.
"""

import os
import requests
from bs4 import BeautifulSoup


def remove_html_tags(text) -> str:
    """Removes HTML tags from a string."""
    soup = BeautifulSoup(text, "html.parser")
    return soup.text.strip()


def download_file(url: str, params: dict, save_dir: str, filename: str) -> str:
    """Downloads a file from a url to the specified location.

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

def read_file(filepath: str) -> str:
    """Load a file from the specified path."""
    try:
        with open(filepath, 'r', encoding = "utf-8") as file:
            return file.read()
        print(f"Info: File loaded successfully from {filepath}.")
    except Exception as e:
        print(f"Info: Failed to load file: {e}")

def make_dir(directory: str) -> None:
    """
    Create a directory if it does not already exist.
    
    :param directory: Path to the directory.
    """
    if not os.path.exists(directory):
        os.makedirs(directory)

def save_file(content: str, filepath: str) -> None:
    """Save content to a file at the specified path."""
    try:
        # Check if the directory exists
        directory = os.path.dirname(filepath)
        if directory and not os.path.exists(directory):
            raise ValueError(f"Directory does not exist: {directory}")

        # Write content to the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
            
        print(f"File saved successfully at {filepath}.")

    except ValueError as ve:
        print(f"Invalid filepath: {ve}")
        raise
    except Exception as e:
        print(f"An unexpected error occurred while saving the file: {e}")
        raise