import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from typing import Optional
from matplotlib.colors import LinearSegmentedColormap
from resources.schemata.method_schema import metric_to_legend
from Utils.Logger import setup_logger

logger = setup_logger("PlotSyntaxValidity", "logs/plot_syntax_validity.log")

# Colorblind-safe IBM palette
ibm_palette = [
    "#648FFF",  # blue
    "#FFB000",  # yellow
    "#785EF0",  # purple
    "#FE6100",  # orange
    "#DC267F",  # pink
    "#009E73",  # green
    "#C0C0C0",  # gray
]

model_order = [
    'meta-llama-3.1-8b-instruct',
    'llama-3.1-sauerkrautlm-70b-instruct',
    'llama-3.3-70b-instruct',
    'mistral-large-instruct',
    'qwen2.5-72b-instruct',
    'qwq-32b',
    'deepseek-r1-distill-llama-70b',
]

def load_and_prepare_data(csv_path: str, mode: Optional[str] = None) -> pd.DataFrame:
    """Return preprocessed DataFrame from CSV file."""
    df = pd.read_csv(csv_path)

    # Filter by mode if specified
    if mode:
        df = df[df["mode"] == mode]

    # Add conversion rate from well-formed Turtle to well-formed SHACL
    df["conversion_rate"] = df["valid_shacl_all"] / df["valid_turtle_all"]

    return df

def plot_syntax_bar_chart(csv_path: str, save_path: Optional[str] = None, mode: Optional[str] = None):
    """
    Plot a bar chart comparing Turtle and SHACL validity across models, with
    conversion rate overlaid as a line plot.
    """
    # Load and prepare data
    df = load_and_prepare_data(csv_path, mode)
    
    # Bar plot for fraction of well-formed Turtle and SHACL
    _, ax = plt.subplots(figsize=(10, 6))
    bar_width = 0.35
    x = range(len(df))
    ax.bar([i - bar_width/2 for i in x], df["valid_turtle_all"], width=bar_width, label=metric_to_legend["valid_turtle_all"], color='#3F64B3') # 648FFF
    ax.bar([i + bar_width/2 for i in x], df["valid_shacl_all"], width=bar_width, label=metric_to_legend["valid_shacl_all"], color='#A2C7FF') # #3F64B3
    ax.set_xticks(x)
    ax.set_xticklabels(df["model"], rotation=45, ha="right")
    ax.set_ylabel("Syntax Accuracy / Conversion Rate")
    ax.set_ylim(0, 1.05)
    
    # Add value labels on top of bars
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", padding=0, fontsize=10, color='black')

    # Line plot for conversion rate on the same axis
    ax.plot(x, df["conversion_rate"], color='#FF9B4D', marker='o', label=metric_to_legend["conversion_rate"], linewidth=2)

    # Add legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='upper left', frameon=False)
    plt.subplots_adjust(right=0.8)
    plt.tight_layout()
    
    plt.show()
    
    # Optionally save the plot
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, format="svg")
        logger.info(f"Saved bar chart for all metrics to {os.path.abspath(save_path)}")
