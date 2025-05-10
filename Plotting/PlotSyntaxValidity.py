import os
import pandas as pd
import matplotlib.pyplot as plt
from typing import Optional, List
from resources.schemata.method_schema import metric_to_legend, models_to_legend, modes_to_legend
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

def load_and_prepare_data(csv_path: str, models: List[str] = None, mode: Optional[str] = None) -> pd.DataFrame:
    """Return preprocessed DataFrame from CSV file."""
    df = pd.read_csv(csv_path)

    # Filter by mode if specified
    if mode:
        df = df[df["mode"] == mode]
        
    # Filter by models if specified
    if models:
        df = df[df["model"].isin(models)]

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
    df = load_and_prepare_data(csv_path=csv_path, mode=mode)

    # Bar plot for proportion of well-formed Turtle and SHACL
    fig, ax = plt.subplots(figsize=(10, 6))

    # Set background and grid lines
    ax.set_facecolor("#f0f0f0")
    ax.grid(True, axis='y', color="white", linewidth=0.5)
    ax.set_axisbelow(True)

    bar_width = 0.35
    x = range(len(df))
    ax.bar([i - bar_width/2 for i in x], df["valid_turtle_all"], width=bar_width, label=metric_to_legend["valid_turtle_all"], color='#3F64B3')  # 648FFF
    ax.bar([i + bar_width/2 for i in x], df["valid_shacl_all"], width=bar_width, label=metric_to_legend["valid_shacl_all"], color='#A2C7FF')  # #3F64B3
    
    ax.set_xticks(x)

    # Convert model names to human-readable labels using the dictionary
    human_readable_labels = [models_to_legend.get(model, model) for model in df["model"]]

    # Update x-axis with human-readable labels
    xtick_labels = [label + "*" if "qwen" in label.lower() else label for label in human_readable_labels]
    ax.set_xticklabels(xtick_labels, rotation=45, ha="right")
    ax.set_ylabel("Syntax Conformance")
    ax.set_ylim(0, 1.05)
    
    # Add value labels on top of bars
    for container in ax.containers:
        ax.bar_label(container, fmt="%.3f", padding=0, fontsize=10, color='black')

    # Add legend
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles, labels, loc='upper right', frameon=False)
    legend = ax.legend(handles, labels, loc='upper right', frameon=True)
    legend.get_frame().set_facecolor("#f0f0f0")
    legend.get_frame().set_edgecolor("#d0d0d0") 
    legend.get_frame().set_linewidth(1.0)

    # Style the plot
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='both', which='both', length=0)
    
    note = "*Third run omitted due to frequent request timeouts."
    ax.text(1.0, -0.15, note,  # move up (closer to axis)
            transform=ax.transAxes,
            ha='right', va='top',
            fontsize=10, color='gray')

    plt.subplots_adjust(bottom=0.8, right=0.8)
    plt.tight_layout()

    # Optionally save the plot
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, format="svg", facecolor=fig.get_facecolor())
        logger.info(f"Saved bar chart for all metrics to {os.path.abspath(save_path)}")
    
    plt.show()


def plot_shacl_conformance_over_exp(csv_path: str,
                                    models: List[str] = ['llama-3.1-sauerkrautlm-70b-instruct',
                                                        'mistral-large-instruct',
                                                        'qwq-32b'],
                                    save_path: Optional[str] = None):
    """
    Plot SHACL conformance (valid_shacl_all) across models and experiments.
    """
    # Load and filter data
    df = pd.read_csv(csv_path)
    df = df[df['model'].isin(models)]
    df = df[df['mode'].isin(['baseline_0ex0fcv', 'fewshot_1ex3fcv', 'cot_1ex3fcv'])]

    # Ensure correct ordering
    mode_order = ['baseline_0ex0fcv', 'fewshot_1ex3fcv', 'cot_1ex3fcv']
    color_map = {
        'baseline_0ex0fcv': '#A2C7FF',
        'fewshot_1ex3fcv': '#FFB000',
        'cot_1ex3fcv': '#FF7F33',
    }

    # Pivot for plotting
    pivot_df = df.pivot(index='model', columns='mode', values='valid_shacl_all').reindex(models)

    # Plot setup
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_facecolor("#f0f0f0")
    ax.grid(True, axis='y', color="white", linewidth=0.5)
    ax.set_axisbelow(True)

    bar_width = 0.2
    x = list(range(len(models)))

    for i, mode in enumerate(mode_order):
        offset = (i - 1) * bar_width  # center bars around each model
        values = pivot_df[mode].values
        ax.bar([pos + offset for pos in x],
               values,
               width=bar_width,
               label=modes_to_legend.get(mode, mode),
               color=color_map[mode])
        
    # Convert model names to human-readable labels using the dictionary
    human_readable_labels = [models_to_legend.get(model, model) for model in models]

    # Update x-axis with human-readable labels
    ax.set_xticks(x)
    ax.set_xticklabels(human_readable_labels)
    ax.set_ylabel("SHACL Syntax Conformance")
    ax.set_ylim(0, 1.05)

    # Add value labels on bars
    for container in ax.containers:
        ax.bar_label(container, fmt="%.3f", padding=2, fontsize=10, color='black')

    # Legend styling
    handles, labels = ax.get_legend_handles_labels()
    legend = ax.legend(handles, labels, loc='upper right', frameon=True)
    legend.get_frame().set_facecolor("#f0f0f0")
    legend.get_frame().set_edgecolor("#d0d0d0")
    legend.get_frame().set_linewidth(1.0)

    # Remove spines and ticks
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='both', which='both', length=0)

    # Layout and save
    plt.tight_layout()
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, format="svg", facecolor=fig.get_facecolor())
        logger.info(f"Saved SHACL bar chart to {os.path.abspath(save_path)}")

    plt.show()
    