""" 
SplitDataset.py

Generate a train and a test split from the selected social benefits.
"""

import os
import random
import argparse
import sys
from Utils.Logger import setup_logger
from Utils.FileHandling import copy_files, validate_input_directory

logger = setup_logger(__name__, log_file="logs/SplitDataset.log")

def setup_split_directories(save_dir: str):
    """Creates 'train' and 'test' directories in the save directory."""
    train_dir = os.path.join(save_dir, 'train')
    test_dir = os.path.join(save_dir, 'test')
    os.makedirs(train_dir, exist_ok=True)
    os.makedirs(test_dir, exist_ok=True)
    return train_dir, test_dir

def shuffle_and_split_files(all_files: list, train_ratio: float) -> tuple:
    """Shuffles and splits files into training and testing sets."""
    random.shuffle(all_files)
    num_train = int(len(all_files) * train_ratio)
    return all_files[:num_train], all_files[num_train:]

def main(social_benefits_dir: str, save_dir: str, train_ratio: float = 0.7):
    """
    Splits files in the input directory into train and test data.

    :param social_:benefits_dir: Directory with selected social benefitrequirements.
    :param save_dir: Directory where splits will be saved.
    :param train_ratio: Ratio of files to include in the training set (default is 0.7).
    :side effects: Creates 'train' and 'test' directories and copies files to them.
    """
    validate_input_directory(social_benefits_dir, logger)
    train_dir, test_dir = setup_split_directories(save_dir)
    
    # If train and test splits already exist, skip splitting
    if os.listdir(train_dir) and os.listdir(test_dir):
        logger.info(f"Train and test splits already exist at {save_dir}")
        return
        
    logger.info(f"Splitting dataset at {social_benefits_dir} with ratio {train_ratio}.")
    
    all_files = [file for file in os.listdir(social_benefits_dir) if os.path.isfile(os.path.join(social_benefits_dir, file))]
    train_files, test_files = shuffle_and_split_files(all_files, train_ratio)

    copy_files(train_files, social_benefits_dir, train_dir)
    copy_files(test_files, social_benefits_dir, test_dir)

    logger.info("Dataset split complete!\n"
                f"Train split: {len(train_files)} files moved to {train_dir}\n"
                f"Test split: {len(test_files)} files moved to {test_dir}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Split a dataset into train and test splits.")
    parser.add_argument("social_benefits_dir", type=str, help="Directory with all administrative service descriptions.")
    parser.add_argument("save_dir", type=str, help="Directory where splits will be saved.")
    parser.add_argument("--train_ratio", type=float, default=0.7, help="Proportion of data to use for training (default: 0.7).")

    args = parser.parse_args()

    main(social_benefits_dir=args.all_services_desc_dir, save_dir=args.save_dir, train_ratio=args.train_ratio)