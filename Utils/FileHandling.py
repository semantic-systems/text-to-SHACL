""" 
FileHandling.py

Utility functions for handling files.
"""
import os
import json
import shutil
import requests
import logging
import subprocess
from typing import Any, Dict


def download_and_save_file(url: str, params: dict, save_dir: str, filename: str) -> str:
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


def save_dict_to_json(data: Dict[Any,Any], save_path: str):
    """Saves the data to a JSON file at the specified path."""
    # Ensure that the save directory exists
    save_dir = os.path.dirname(save_path)
    os.makedirs(save_dir, exist_ok=True)
    with open(save_path, 'w', encoding='utf-8') as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def copy_files(file_list: list, src_dir: str, dest_dir: str):
    """
    Copies files from the source directory to the destination directory.
    
    :param file_list: List of files to copy.
    :param src_dir: Source directory.
    :param dest_dir: Destination directory
    """
    for file in file_list:
        shutil.copy(os.path.join(src_dir, file), os.path.join(dest_dir, file))


def validate_input_directory(input_dir: str, logger: logging.Logger):
    """Validates that the input directory exists, is a directory, and is not empty."""
    if not os.path.exists(input_dir):
        logger.error(f"Input directory '{input_dir}' does not exist.")
        raise FileNotFoundError(f"Input directory '{input_dir}' does not exist.")
    if not os.path.isdir(input_dir):
        logger.error(f"Input path '{input_dir}' is not a directory.")
        raise NotADirectoryError(f"Input path '{input_dir}' is not a directory.")
    if not os.listdir(input_dir):
        logger.error(f"Input directory '{input_dir}' is empty.")
        raise ValueError(f"Input directory '{input_dir}' is empty.")


def save_file(content: str, filepath: str, logger: logging.Logger) -> None:
    """Saves content to a file at the specified path."""
    try:
        # Ensure save directory exists
        directory = os.path.dirname(filepath)
        os.makedirs(directory, exist_ok=True)

        # Write content to the file
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        logger.info(f"File saved to: {filepath}")
    except Exception as e:
        logger.error(f"An error occurred while saving the file: {e}")


def load_file(file_path: str, logger: logging.Logger, as_json: bool = False) -> Any:
    """Return file content as a string or JSON object using utf-8 encoding."""
    try:
        with open(file_path, 'r', encoding = "utf-8") as file:
            return json.load(file) if as_json else file.read()
    except FileNotFoundError as e:
        logger.error(f"Failed to load prompt component. File not found: {file_path}")
        raise ValueError


def convert_md_to_pdf(md_file, output_folder, new_file_name):
    """Converts a markdown file to a PDF and saves the PDF to the output folder."""
    html_file = os.path.join(output_folder, new_file_name + ".html")
    pdf_file = os.path.join(output_folder, new_file_name + ".pdf")

    subprocess.run(["pandoc", md_file, "-o", html_file], check=True)
    # Linux: subprocess.run(["pandoc", html_file, "-o", pdf_file, "--pdf-engine=xelatex"], check=True)
    subprocess.run(["pandoc", html_file, "-o", pdf_file], check=True)

    os.remove(html_file)