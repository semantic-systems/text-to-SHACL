""" 
Visualization.py

Visualize the evaluation results.
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
from typing import List
from matplotlib.colors import LinearSegmentedColormap
from resources.schemata.method_schema import avg_syntax_metrics, avg_all_metrics, avg_valid_only_metrics, metric_to_legend

# IBM Design colorblind-safe palette
ibm_palette = [
    "#648FFF", "#FFB000", "#785EF0", "#FE6100",
    "#DC267F", "#009E73", "#C0C0C0",
]

def load_and_prepare_data(csv_path: str):
    df = pd.read_csv(csv_path)
    df["graph_edit_distance_all"] = 1 - df["graph_edit_distance_all"]
    df["graph_edit_distance_valid_only"] = 1 - df["graph_edit_distance_valid_only"]
    return df

def plot_bar_chart(df, metrics, title):
    # Compute sum across selected metrics and sort by it (descending)
    df["__model_score__"] = df[metrics].sum(axis=1)
    df = df.sort_values("__model_score__", ascending=False).drop(columns="__model_score__")

    # Melt and map metric names to legend labels
    melted = df.melt(id_vars=["model"], value_vars=metrics,
                     var_name="Metric", value_name="Score")
    melted["Metric"] = melted["Metric"].map(metric_to_legend)

    plt.figure(figsize=(12, 6))
    sns.set_theme(style="whitegrid")
    sns.barplot(data=melted, x="model", y="Score", hue="Metric", palette=ibm_palette[:len(metrics)])
    plt.title(title)
    plt.xlabel("Model")
    plt.ylabel("Score")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

def plot_inference_time(df: pd.DataFrame):
    df = df.sort_values("inference_time", ascending=True)
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="whitegrid")
    sns.set_palette([ibm_palette[0]] * len(df))
    sns.barplot(data=df, x="model", y="inference_time", hue="model")
    plt.title("Inference Time by Model")
    plt.ylabel("Inference Time (seconds)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.show()

def plot_heatmap(df: pd.DataFrame, metrics: List[str], title: str):
    custom_cmap = LinearSegmentedColormap.from_list("orange_to_blue", ["#DC267F", "#648FFF"])
    data = df.set_index("model")[metrics]
    # normalized = (data - data.min()) / (data.max() - data.min())
    data.columns = [metric_to_legend.get(m, m) for m in data.columns]
    data.columns = data.columns
    
    plt.figure(figsize=(12, 6))
    sns.set_theme(style="white")
    sns.heatmap(
        data,
        annot=data.round(2),
        cmap=custom_cmap,
        linewidths=0.5,
        cbar_kws={'label': 'Normalized Score'}
    )
    plt.title(title)
    plt.tight_layout()
    plt.figtext(0.99, 0.01, "* GED is inverted", horizontalalignment='right', fontsize=12)
    plt.show()

def plot_summary_metrics(csv_path: str):
    if not os.path.exists(csv_path):
        raise FileNotFoundError(f"File not found: {csv_path}")

    df = load_and_prepare_data(csv_path)
    
    # Drop discarded models
    # models_to_drop = ['deepseek-r1-distill-llama-70b', 'llama-3.3-70b-instruct', 'qwen2.5-72b-instruct']
    # df = df[~df["model"].isin(models_to_drop)]
    
    # Syntax metrics by model (valid Turtle and SHACL)
    plot_bar_chart(df, avg_syntax_metrics, "Syntax Validity Scores by Model")
    
    # Comparative metrics by model (all files)
    plot_bar_chart(df, avg_all_metrics, "Comparison with Groundtruth by Model (All files)")
    plot_heatmap(df, avg_all_metrics, "Performance Overview (All files)")
    
    # Comparative metrics by model (valid SHACL files only)
    plot_bar_chart(df, avg_valid_only_metrics, "Comparison with Groundtruth by Model (Valid SHACL files only)")
    plot_heatmap(df, avg_valid_only_metrics, "Performance Overview (Valid SHACL files only)")
    
    # Inference time by model
    plot_inference_time(df)    