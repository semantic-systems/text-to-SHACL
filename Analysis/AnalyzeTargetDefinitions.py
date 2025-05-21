"""
AnalyzeTargetDefinitions.py

Functions for analyzing SHACL target definitions across experiment runs:
- ratio of SHACL graphs with user target node
- distribution of SHACL target types
- visualization in a heatmap
"""

import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from collections import defaultdict, Counter
from rdflib import Graph, URIRef
from typing import Tuple, Dict
from resources.schemata.method_schema import models_to_legend
from matplotlib.colors import LinearSegmentedColormap

# SHACL predicates and the user node URI
TARGET_NODE = URIRef("http://www.w3.org/ns/shacl#targetNode")
TARGET_CLASS = URIRef("http://www.w3.org/ns/shacl#targetClass")
TARGET_SUBJECTS = URIRef("http://www.w3.org/ns/shacl#targetSubjectsOf")
TARGET_OBJECTS = URIRef("http://www.w3.org/ns/shacl#targetObjectsOf")
USER_NODE = URIRef("https://foerderfunke.org/default#User")


def analyze_target_definitions(file_path: str) -> Tuple[bool, Counter]:
    """
    Analyze target definitions in a single SHACL shapes graphs.
    
    :param file_path: Path to the shapes graph (.ttl)
    :return: Tuple with the presence of the user target (True/False),
                and the counts of each target type.
    """
    g = Graph()
    g.parse(file_path, format="turtle")

    has_user_target = False
    target_type_counts = Counter()

    for s, p, o in g:
        if p == TARGET_NODE and o == USER_NODE:
            has_user_target = True
        if p in [TARGET_NODE, TARGET_CLASS, TARGET_SUBJECTS, TARGET_OBJECTS]:
            target_type_counts[p] += 1

    return has_user_target, target_type_counts

def analyze_all_runs(results_dir: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Analyze the target definitions in all experiment runs.
    
    :param results_dir: Path to the top-level results directory.
    :return: Two DataFrames:
                - Proportion of graphs with user target (per model and run)
                - Distribution of SHACL target types (per model and run)
    """
    model_graph_counts: Dict[Tuple[str, str], int] = defaultdict(int)
    model_user_target_counts: Dict[Tuple[str, str], int] = defaultdict(int)
    model_target_type_totals: Dict[Tuple[str, str], Counter] = defaultdict(Counter)

    for run in os.listdir(results_dir):
        run_path = os.path.join(results_dir, run)
        prompt = run.split("_")[0]
        if not os.path.isdir(run_path):
            continue

        for model in os.listdir(run_path):
            model_path = os.path.join(run_path, model)
            if not os.path.isdir(model_path):
                continue

            parsed_output_path = os.path.join(model_path, "output", "parsed_output")
            if not os.path.exists(parsed_output_path) or len(os.listdir(parsed_output_path)) == 0:
                print(f"Warning: No parsed output found for {model_path}")
                continue

            for file in os.listdir(parsed_output_path):
                if not file.endswith(".ttl"):
                    continue
                file_path = os.path.join(parsed_output_path, file)
                has_user_target, target_counts = analyze_target_definitions(file_path)

                key = (run, model)
                model_graph_counts[key] += 1
                if has_user_target:
                    model_user_target_counts[key] += 1
                model_target_type_totals[key].update(target_counts)

    # Create DataFrame: User Target Proportion
    user_target_df = pd.DataFrame([
        {
            "experiment": run,
            "model": model,
            "Total Graphs": model_graph_counts[(run, model)],
            "Total with User Target": model_user_target_counts[(run, model)],
            "Proportion with User Target": model_user_target_counts[(run, model)] / model_graph_counts[(run, model)]
        }
        for (run, model) in sorted(model_graph_counts)
    ])

    # Create DataFrame: Target Type Proportions
    target_types_df = pd.DataFrame([
        {
            "experiment": run,
            "model": model,
            "Total Targets": sum(counts.values()),
            "targetNode (%)": counts[TARGET_NODE] / sum(counts.values()) if sum(counts.values()) else 0,
            "targetClass (%)": counts[TARGET_CLASS] / sum(counts.values()) if sum(counts.values()) else 0,
            "targetSubjectsOf (%)": counts[TARGET_SUBJECTS] / sum(counts.values()) if sum(counts.values()) else 0,
            "targetObjectsOf (%)": counts[TARGET_OBJECTS] / sum(counts.values()) if sum(counts.values()) else 0,
        }
        for (run, model), counts in model_target_type_totals.items()
    ])

    return user_target_df, target_types_df


def aggregate_user_target_proportions(csv_path: str, save_path: str = None) -> pd.DataFrame:
    """
    Computes the mean and standard deviation of the ratio of generated RDF graphs
    with the correct user target node, grouped by prompt and model.

    :param csv_path: Path to input CSV file.
    :param save_path: If provided, saves the result to this CSV file.

    :return: DataFrame with cols ['prompt', 'model', 'user_target_mean', 'user_target_std']
    """
    df = pd.read_csv(csv_path)

    # Extract prompt from the experiment field
    df["prompt"] = df["experiment"].str.extract(r"^(baseline|fewshot|cot)")

    # Group by prompt and model, compute mean and std
    grouped = df.groupby(["prompt", "model"])["Proportion with User Target"].agg(
        user_target_mean="mean",
        user_target_std="std"
    ).reset_index()

    # Optionally save to CSV
    if save_path:
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        grouped.to_csv(save_path, index=False)
        print(f"Saved aggregated results to {os.path.abspath(save_path)}")

    return grouped


def plot_target_definitions_heatmap(target_data_path: str, evaluation_metrics_path: str, main_models_only: bool = True,save_path: str = None):
    """
    Create a heatmap with models on the y-axis and prompts on the x-axis, and three subplots:
    - proportion of generated SHACL graphs with correctly defined target node user
    - validation recall over well-formed SHACL graphs
    - validation precision over well-formed SHACL graphs
    
    :param target_data_path: Path to the CSV file with target definition distributions.
    :param evaluation_metrics_path: Path to the CSV file with evaluation results per prompt.
    :param main_models_only: If True, only include the main models in the heatmap.
    :save_path: Path to save the heatmap image.
    """
    # Load data
    df1 = pd.read_csv(target_data_path)
    df2 = pd.read_csv(evaluation_metrics_path)
    df2['prompt'] = df2['mode'].str.extract(r'^(baseline|fewshot|cot)')

    # Fix model and prompt order
    prompt_order = ["baseline", "fewshot", "cot"]
    
    main_models = ["mistral-large-instruct", "llama-3.1-sauerkrautlm-70b-instruct", "qwq-32b"]
    if main_models_only:
        ordered_models = main_models
        figsize = (15, 5)
    else:
        all_models = sorted(set(df1["model"]) | set(df2["model"]))
        other_models = [m for m in all_models if m not in main_models]
        ordered_models = other_models + main_models
        figsize = (15, 10)

    # Abbreviated labels, adding * to Qwen
    abbreviated_index = [
        models_to_legend.get(model, model) + ("*" if model == "qwen2.5-72b-instruct" else "")
        for model in ordered_models
    ]

    # Create subplots for each metric
    _, axes = plt.subplots(1, 3, figsize=figsize, sharey=True)
    metrics = [
        ("user_target", df1, "User Node Target Ratio"),
        ("validation_recall_valid_only", df2, "Validation Recall"),
        ("validation_precision_valid_only", df2, "Validation Precision")
    ]

    for ax, (metric_base, df, title) in zip(axes, metrics):
        mean_col = f"{metric_base}_mean"
        std_col = f"{metric_base}_std"

        pivot_mean = df.pivot(index="model", columns="prompt", values=mean_col) \
                    .reindex(index=ordered_models, columns=prompt_order)
        pivot_std = df.pivot(index="model", columns="prompt", values=std_col) \
                    .reindex(index=ordered_models, columns=prompt_order)

        annot_data = pivot_mean.copy().astype(str)

        for row in pivot_mean.index:
            for col in pivot_mean.columns:
                mean = pivot_mean.loc[row, col]
                std = pivot_std.loc[row, col]
                if pd.notna(mean) and pd.notna(std):
                    annot_data.loc[row, col] = f"{mean:.2f} ± {std:.2f}"
                else:
                    annot_data.loc[row, col] = "-"

        sns.heatmap(
            pivot_mean,
            annot=annot_data,
            fmt="",
            cmap="Blues",
            linewidths=0.5,
            linecolor='white',
            cbar=False,
            vmin=0,
            vmax=1,
            ax=ax
        )

        # Set titles and labels
        ax.set_title(title, fontsize=16, pad=20)
        ax.set_xlabel("")
        ax.set_xticklabels(["Base", "FS", "CoT"])
        ax.set_yticklabels(abbreviated_index, rotation=0, fontsize=10)
        ax.set_ylabel("")
    
    subplot_axes = [axes[1], axes[2]]
    for ax in subplot_axes:
        ax.tick_params(axis='y', which='both',length=0)
    
    # Add footnote for QwQ
    if not main_models_only:
        note = "*Third baseline run omitted due to frequent request timeouts."
        ax.text(1, -0.15, note,
                transform=ax.transAxes,
                ha='right', va='top',
                fontsize=10, color='gray')
        
    plt.tight_layout()
    plt.subplots_adjust(wspace=0.1) 
    
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)

    plt.show()