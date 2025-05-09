import os
import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional
from resources.schemata.method_schema import var_name_to_fig_label
from Utils.Logger import setup_logger

logger = setup_logger("PlotSyntaxValidity", "logs/plot_syntax_validity.log")

def load_and_prepare_data(csv_path: str, mode: Optional[str] = None) -> pd.DataFrame:
    """Return preprocessed DataFrame from CSV file."""
    df = pd.read_csv(csv_path)

    # Filter by mode if specified
    if mode:
        df = df[df["mode"] == mode]

    # Add conversion rate from well-formed Turtle to well-formed SHACL
    df["conversion_rate"] = df["valid_shacl_all"] / df["valid_turtle_all"]

    # Reorder models based on similarity
    model_order = [
        'meta-llama-3.1-8b-instruct',
        'llama-3.1-sauerkrautlm-70b-instruct',
        'llama-3.3-70b-instruct',
        'mistral-large-instruct',
        'qwen2.5-72b-instruct',
        'qwq-32b',
        'deepseek-r1-distill-llama-70b',
    ]

    # Reorder the dataframe based on the model_order list
    df["model"] = pd.Categorical(df["model"], categories=model_order, ordered=True)
    df = df.sort_values("model")

    return df

def plot_syntax_bar_chart(csv_path: str, save_path: Optional[str] = None, mode: Optional[str] = None):
    """
    Plot a bar chart comparing Turtle and SHACL validity across models, with
    conversion rate overlaid as a line plot.
    """
   # Load and prepare data
    df = load_and_prepare_data(csv_path, mode)

    # Bar plot for fraction of well-formed Turtle and SHACL
    fig, ax = plt.subplots(figsize=(10, 6))

    # Set background and grid lines
    ax.set_facecolor("#f0f0f0")
    ax.grid(True, axis='y', color="white", linewidth=0.5)
    ax.set_axisbelow(True)

    bar_width = 0.35
    x = range(len(df))
    ax.bar([i - bar_width/2 for i in x], df["valid_turtle_all"], width=bar_width, label=var_name_to_fig_label["valid_turtle_all"], color='#3F64B3')  # 648FFF
    ax.bar([i + bar_width/2 for i in x], df["valid_shacl_all"], width=bar_width, label=var_name_to_fig_label["valid_shacl_all"], color='#A2C7FF')  # #3F64B3
    ax.set_xticks(x)
    xtick_labels = [label + "*" if "qwen" in label.lower() else label for label in df["model"]]
    ax.set_xticklabels(xtick_labels, rotation=45, ha="right")
    ax.set_ylabel("Syntax Conformance")
    ax.set_ylim(0, 1.05)

    # Add value labels on top of bars
    for container in ax.containers:
        ax.bar_label(container, fmt="%.2f", padding=0, fontsize=10, color='black')

    # Line plot for conversion rate on the same axis
    #ax.plot(x, df["conversion_rate"], color='#FF9B4D', marker='^', label=metric_to_legend["conversion_rate"], linewidth=1)

    # Add legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='upper left', frameon=False)
    legend = ax.legend(handles, labels, loc='upper left', frameon=True)
    legend.get_frame().set_facecolor("#f0f0f0")
    legend.get_frame().set_edgecolor("#d0d0d0") 
    legend.get_frame().set_linewidth(1.0)

    # Style the plot
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='both', which='both', length=0)
    
    note = "*Third run omitted due to frequent request timeouts."
    ax.text(1.0, -0.5, note,
            transform=ax.transAxes,
            ha='right', va='top',
            fontsize=10, color='gray')

    # Adjust the layout to avoid clipping
    plt.subplots_adjust(bottom=0.5, right=0.8)
    plt.tight_layout()

    # Optionally save the plot
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, format="svg", facecolor=fig.get_facecolor())
        logger.info(f"Saved bar chart for all metrics to {os.path.abspath(save_path)}")
    
    plt.show()