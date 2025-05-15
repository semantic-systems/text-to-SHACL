import random
import json
import time
import os
import argparse
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.cm as cm
import numpy as np
from typing import List, Dict, Any
from Pipeline.Evaluation.GraphMatch import GraphMatcher
from Utils.Logger import setup_logger

# Constants
TIMEOUTS = [60, 120, 180, 240, 300, 360, 420, 480, 540, 600]

# Logging
logger = setup_logger("ged_timeout_logger", "logs/ged_timeout_inspection.log")

def get_ged_timeout_data(raw_output_path: str, timeouts: List[int] = TIMEOUTS, k: int = 5) -> List[Dict[str,Any]]:
    """
    Computes GED between n randomly sampled, LLM generated SHACL graphs at 
    various timeouts.

    :param raw_output_path: Path to results JSON from which to sample graphs.
    :param timeouts: List of timeout values in seconds.
    :param k: Number of graphs to sample.
    
    :return: List of dictionaries with timeout, GED, runtime, and file paths.
    """
    timeouts = [360, 420, 480, 540, 600]
    
    # Randomly sample k outputs that produced valid turtle from the results
    with open(raw_output_path, 'r', encoding = "utf-8") as f:
        raw_output = json.load(f)
    valid_turtle_items = [item for item in raw_output if item['metadata'].get('valid_turtle') == 1]
    sampled_items = random.sample(valid_turtle_items, k=k, seed=42)

    ged_timeout_data = []
    for timeout in timeouts:
        logger.info(f"Computing GED for timeout: {timeout} seconds")
        for i, item in enumerate(sampled_items):
            logger.info(f"Processing file {i+1}/{len(sampled_items)}")
            
            # Get Path to SHACL gen and SHACL gold
            gen_path = item["metadata"]["parsed_output_path"]
            input_path = item["metadata"]["test_filepath"]
            gold_path = input_path.replace("requirements_texts", "shacl_gold").replace(".json", ".ttl")
            gm = GraphMatcher(gold_path, gen_path, "logs/ged_timeouts_tests.log")
            
            # Run GED with current timeout
            start_time = time.time()
            ged = gm.compute_ged(timeout=timeout)
            elapsed_time = time.time() - start_time
            timeout_data = {
                "Timeout": timeout,
                "GED": ged,
                "Runtime": elapsed_time,
                "SHACL gold": gold_path,
                "SHACL gen": gen_path,
            }
            ged_timeout_data.append(timeout_data)
            
    return ged_timeout_data

def save_ged_timeout_data(data: List[Dict[str, Any]], data_output_path: str):
    """
    Saves the GED timeout data to a JSON file. If the file already exists,
    appends the new data to it.
    
    :param data: Data on GED computation for different timeouts.
    :param data_output_path: Path to save the GED timeout data.
    """
    if os.path.exists(data_output_path):
        with open(data_output_path, "r", encoding="utf-8") as f:
            existing_data = json.load(f)
    else:
        existing_data = []
    existing_data.extend(data)
    with open(data_output_path, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=4)
    
    logger.info(f"GED timeout data saved to {data_output_path}")

def plot_ged_timeout_data(data: List[Dict[str, Any]], figure_output_path: str = None):
    """
    Plots the GED in relation to timeout for the given data. Optionally
    saves the figure to the specified path.
    
    :param data: Data on GED computation for different timeouts.
    :param figure_output_path: Optional path to save the figure.
    """
    # Prepare dataframe
    df = pd.DataFrame(data)
    df['SHACL gold name'] = df['SHACL gold'].apply(lambda x: x.split('/')[-1])
    pivot_df = df.pivot_table(index='Timeout', columns='SHACL gold name', values='GED')

    # Plot line for individual benefits in shades of blue
    colors = cm.Blues(np.linspace(0.4, 0.9, pivot_df.shape[1]))
    ax = pivot_df.plot(color=colors, marker='o', markersize=4, linewidth=1, legend=False)

    # ax = pivot_df.plot(color=colors, marker='o', legend=False)

    # Plot the mean line in red
    pivot_df.mean(axis=1).plot(ax=ax, color='red', linestyle='--', marker='o',
                           markersize=4, linewidth=1.5, label='Mean GED')

    #pivot_df.mean(axis=1).plot(ax=ax, color='red', linestyle='--', marker='o', label='Mean GED')

    # Style background
    ax.set_facecolor("#f0f0f0")
    ax.grid(True, axis='y', color="white", linewidth=0.5)
    ax.set_axisbelow(True)
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='both', which='both', length=0)
    ax.set_ylim(0.2, 1)
    
    # Format plot
    plt.xlabel("Timeout (seconds)")
    plt.ylabel("Graph Edit Distance")
    plt.legend(loc='upper right', ncol=2)
    plt.tight_layout()
    
    # Optionally save the figure as svg
    if figure_output_path:
        plt.savefig(figure_output_path, format='svg', bbox_inches='tight')
        logger.info(f"Figure saved to {figure_output_path}")

    plt.show()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Compute and plot GED vs Timeout")
    parser.add_argument("--timeouts", type=List, required=True, help="List of GED timeouts in seconds.")
    parser.add_argument("--k", type=int, required=True, help="Number of graphs to sample for GED computation.")
    parser.add_argument("--results_path", type=str, required=True, help="Path to a ''raw_output.json' with results for one experiment.")
    parser.add_argument("--data_output_path", type=str, required=True, help="Path to save the GED timeout data.")
    parser.add_argument("--figure_output_path", type=str, required=True, help="Path to save the figure.")
    args = parser.parse_args()

    ged_timeout_data = get_ged_timeout_data(
        raw_output_path=args.raw_output_path, timeouts=args.timeouts, k=args.k
        )
    save_ged_timeout_data(
        data=ged_timeout_data, data_output_path=args.data_output_path
        )
    plot_ged_timeout_data(ged_timeout_data, args.figure_output_path)