""" 
dataset.py

Generate a train and a test split from all selected social benefits.
"""

import os
import sys
import shutil
import random


def split_dataset(input_dir: str, output_dir: str, train_ratio: float = 0.7) -> None:
    """Splits files in the input directory into train and test data.

    :param input_dir: Path to the directory containing all input files.
    :param output_dir: Path to the directory where the dataset will be saved.
    :param train_ratio: Ratio of files to include in the training set (default is 0.7).
    """
    train_dir = os.path.join(output_dir, 'train')
    test_dir = os.path.join(output_dir, 'test')

    # Ensure the train and test directories exist in the output directory
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)

    # Get a list of all files in the input directory
    all_files = [file for file in os.listdir(
        input_dir) if os.path.isfile(os.path.join(input_dir, file))]

    # Shuffle the file list for a pseudo-random split
    random.shuffle(all_files)

    # Calculate the number of train and test files
    total_files = len(all_files)
    num_train = int(total_files * train_ratio)
    num_test = total_files - num_train

    # Split the files into training and testing sets
    train_files = all_files[:num_train]
    test_files = all_files[num_train:]

    # Copy files to the train and test directories
    for file in train_files:
        shutil.copy(os.path.join(input_dir, file),
                    os.path.join(train_dir, file))

    for file in test_files:
        shutil.copy(os.path.join(input_dir, file),
                    os.path.join(test_dir, file))

    print("Info: Dataset split complete. "
          f"{num_train} files moved to 'train' and {num_test} files moved to 'test'.")


if __name__ == "__main__":
    if len(sys.argv) == 3:
        split_dataset(input_dir=sys.argv[1], output_dir=sys.argv[2])
    else:
        print(f'Usage: {sys.argv[0]} <Input directory> <Output directory>')
