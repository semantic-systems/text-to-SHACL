"""
PlotSyntaxValidity.py

Functions for visualizing proportion of LLM outputs with well-formed Turtle 
and SHACL as barplots.
"""

import os
import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.lines as mlines
from typing import Optional, List
from resources.schemata.method_schema import metric_to_legend, models_to_legend, modes_to_legend


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
    """Return preprocessed DataFrame from CSV file.
    
    :param csv_path: Path to config-level evaluation results.
    :param models: List of models to filter by.
    :param mode: Mode to filter by (e.g., baseline_0ex0fcv).
    
    :return: DataFrame with filtered and sorted data.
    """
    df = pd.read_csv(csv_path)

    # Filter by mode if specified
    if mode:
        df = df[df["mode"] == mode]
        
    # Filter by models if specified
    if models:
        df = df[df["model"].isin(models)]

    # Reorder models based on type
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
    
    # Reset the index
    df.reset_index(drop=True, inplace=True)
    return df


def plot_syntax_bar_chart(csv_path: str, save_path: Optional[str] = None, mode: Optional[str] = None):
    """
    Plot bar chart:
        - x_axis: model names (main models)
        - y_axis: proportion of well-formed LLM outputs
        - bars: language (Turtle and SHACL)
        - error bars: +/- 1SD for each bar
    
    :param csv_path: Path to config-level evaluation results.
    :param save_path: Path to save the plot.
    :param mode: Mode to filter by (e.g., baseline_0ex0fcv).
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

    # Extract mean and STD columns
    turtle_mean = df["valid_turtle_all_mean"]
    turtle_sd = df["valid_turtle_all_std"]
    shacl_mean = df["valid_shacl_all_mean"]
    shacl_sd = df["valid_shacl_all_std"]

    # Turtle bars
    ax.bar(
        [i - bar_width/2 for i in x],
        turtle_mean,
        width=bar_width,
        label=metric_to_legend["valid_turtle_all"],
        color='#3F64B3',
        yerr=turtle_sd,
        capsize=4,
        error_kw=dict(lw=1.2, ecolor='black')
    )
    # SHACL bars
    ax.bar(
        [i + bar_width/2 for i in x],
        shacl_mean,
        width=bar_width,
        label=metric_to_legend["valid_shacl_all"],
        color='#A2C7FF',
        yerr=shacl_sd,
        capsize=4,
        error_kw=dict(lw=1.2, ecolor='black')
    )

    ax.set_xticks(x)

    # Convert model names to human-readable labels
    human_readable_labels = [models_to_legend.get(model, model) for model in df["model"]]
    xtick_labels = [label + "*" if "qwen" in label.lower() else label for label in human_readable_labels]
    ax.set_xticklabels(xtick_labels, rotation=45, ha="right")
    ax.set_ylabel("Syntax Conformance")
    ax.set_ylim(0, 1.05)

    # Add mean value labels on top of the error bars
    for i in range(len(df)):
        turtle_x = i - bar_width / 2
        shacl_x = i + bar_width / 2
        turtle_top = turtle_mean[i] + turtle_sd[i]
        shacl_top = shacl_mean[i] + shacl_sd[i]

        ax.text(
            turtle_x,
            turtle_top + 0.01,
            f"{turtle_mean[i]:.3f}",
            ha='center', va='bottom',
            fontsize=9, color='black'
        )
        ax.text(
            shacl_x,
            shacl_top + 0.01,
            f"{shacl_mean[i]:.3f}",
            ha='center', va='bottom',
            fontsize=9, color='black'
        )

    # Add legend
    std_handle = mlines.Line2D([], [], color='black', linewidth=1.2, label='± SD')
    handles, labels = ax.get_legend_handles_labels()
    handles.append(std_handle)
    labels.append('± SD')
    
    legend = ax.legend(handles, labels, loc='upper right', frameon=True)
    legend.get_frame().set_facecolor("#f0f0f0")
    legend.get_frame().set_edgecolor("#d0d0d0")
    legend.get_frame().set_linewidth(1.0)

    # Style the plot
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='both', which='both', length=0)

    # Add note
    note = "*Third run omitted due to frequent request timeouts."
    ax.text(1.0, -0.15, note,
            transform=ax.transAxes,
            ha='right', va='top',
            fontsize=10, color='gray')

    plt.subplots_adjust(bottom=0.8, right=0.8)
    plt.tight_layout()

    # Optionally save the plot
    if save_path:
        plt.savefig(save_path, format="svg", facecolor=fig.get_facecolor())
        print(f"Saved syntax conformance bar chart to {os.path.abspath(save_path)}")
    
    plt.show()



def plot_shacl_conformance_over_exp(csv_path: str,
                                    models: List[str] = ['llama-3.1-sauerkrautlm-70b-instruct',
                                                        'mistral-large-instruct',
                                                        'qwq-32b'],
                                    save_path: Optional[str] = None):
    """
    Plot bar chart:
        - x_axis: model names (main models)
        - y_axis: proportion of well-formed SHACL
        - bars: different modes (baseline, fewshot, cot)
        - error bars: +/- 1SD for each bar
        
    :param csv_path: Path to config-level evaluation results.
    :param models: List of models to filter by.
    :param save_path: Path to save the plot.
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

    # Initialize plot
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.set_facecolor("#f0f0f0")
    ax.grid(True, axis='y', color="white", linewidth=0.5)
    ax.set_axisbelow(True)

    bar_width = 0.2
    x = list(range(len(models)))

    for i, mode in enumerate(mode_order):
        offset = (i - 1) * bar_width
        mean_col = "valid_shacl_all_mean"
        std_col = "valid_shacl_all_std"

        values = df[df['mode'] == mode][mean_col].values
        errors = df[df['mode'] == mode][std_col].values

        bars = ax.bar([pos + offset for pos in x],
                      values,
                      width=bar_width,
                      label=modes_to_legend.get(mode, mode),
                      color=color_map[mode],
                      yerr=errors,
                      capsize=4,
                      error_kw=dict(lw=1.2, ecolor='black'))

        # Add value labels on top of error bars
        for xi, val, err in zip([pos + offset for pos in x], values, errors):
            ax.text(
                xi,
                val + err + 0.01,
                f"{val:.3f}",
                ha='center', va='bottom',
                fontsize=9, color='black'
            )

    # X-axis labelsd
    human_readable_labels = [models_to_legend.get(model, model) for model in models]
    ax.set_xticks(x)
    ax.set_xticklabels(human_readable_labels)
    ax.set_ylabel("SHACL Syntax Conformance")
    ax.set_ylim(0, 1.05)

    # Add custom error bar legend entry
    std_handle = mlines.Line2D([], [], color='black', linewidth=1.2, label='± SD')
    handles, labels = ax.get_legend_handles_labels()
    handles.append(std_handle)
    labels.append('± SD')

    legend = ax.legend(handles, labels, loc='upper right', frameon=True)
    legend.get_frame().set_facecolor("#f0f0f0")
    legend.get_frame().set_edgecolor("#d0d0d0")
    legend.get_frame().set_linewidth(1.0)

    # Remove spines and ticks
    for spine in ax.spines.values():
        spine.set_visible(False)
    ax.tick_params(axis='both', which='both', length=0)

    plt.tight_layout()

    # Save if needed
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        plt.savefig(save_path, format="svg", facecolor=fig.get_facecolor())
        print(f"Saved SHACL conformance bar chart to {os.path.abspath(save_path)}")

    plt.show()
    