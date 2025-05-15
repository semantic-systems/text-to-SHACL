import os
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
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
    """Analyze target definitions in a single SHACL Turtle file."""
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

def analyze_all_runs(data_root: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    """
    Analyze the target definitions in all experiment runs and return two DataFrames:
    - Proportion of graphs with user target (per model and run)
    - Distribution of SHACL target types (per model and run)
    """
    model_graph_counts: Dict[Tuple[str, str], int] = defaultdict(int)
    model_user_target_counts: Dict[Tuple[str, str], int] = defaultdict(int)
    model_target_type_totals: Dict[Tuple[str, str], Counter] = defaultdict(Counter)

    for run in os.listdir(data_root):
        run_path = os.path.join(data_root, run)
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

def summarize_by_prompt(df: pd.DataFrame) -> pd.DataFrame:
    """Average the DataFrame over runs by prompt."""
    df['prompt'] = df['experiment'].apply(lambda x: x.split('_')[0])

    # Aggregate: sum Total Graphs, mean the rest
    avg_results = df.groupby(['prompt', 'model'], as_index=False).agg({
        'Total Graphs': 'sum',
        'Total with User Target': 'sum',
        'Proportion with User Target': 'mean'
    })
    
    # Add micro average
    avg_results['Proportion with User Target (Micro)'] = (
        avg_results['Total with User Target'] / avg_results['Total Graphs']
    )

    return avg_results

def plot_heatmap(target_data_path: str, evaluation_metrics_path: str, save_path: str = None):
    """Create a heatmap with models on the y-axis and prompts on the x-axis, and three subplots:
    - proportion of generated SHACL graphs with correctly defined target node user
    - validation recall over well-formed SHACL graphs
    - validation precision over well-formed SHACL graphs
    """
    # Create cmap
    light_blue = "#c1d2ff"
    dark_blue = "#00278e"
    custom_cmap = LinearSegmentedColormap.from_list("custom_blue", [light_blue, dark_blue])
    sns.set_theme(style="white")

    # Load data
    df1 = pd.read_csv(target_data_path)
    df2 = pd.read_csv(evaluation_metrics_path)

    # Fix model and prompt order
    prompt_order = ["baseline", "fewshot", "cot"]
    priority_models = ["mistral-large-instruct", "llama-3.1-sauerkrautlm-70b-instruct", "qwq-32b"]
    all_models = sorted(set(df1["model"]) | set(df2["model"]))
    other_models = [m for m in all_models if m not in priority_models]
    ordered_models = other_models + priority_models
    ordered_models = priority_models

    # Abbreviated labels, adding * to QwQ
    abbreviated_index = [
        models_to_legend.get(model, model) + ("*" if model == "qwq-32b" else "")
        for model in ordered_models
    ]

    # Create subplots for each metric
    # fig, axes = plt.subplots(1, 3, figsize=(18, 8), sharey=True)
    _, axes = plt.subplots(1, 3, figsize=(18,5), sharey=True)
    metrics = [
        ("Proportion with User Target", df1, "Proportion with User Node Target"),
        ("validation_recall_valid_only", df2, "Validation Recall"),
        ("validation_precision_valid_only", df2, "Validation Precision")
    ]

    for ax, (value_col, df, title) in zip(axes, metrics):
        pivot = df.pivot(index="model", columns="prompt", values=value_col) \
                .reindex(index=ordered_models, columns=prompt_order)

        annot_data = pivot.copy().applymap(lambda x: "-" if pd.isna(x) else f"{x:.3f}")

        sns.heatmap(
            pivot,
            annot=annot_data,
            fmt="",
            cmap=custom_cmap,
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
           

    # Add footnote for QwQ
    note = "*Third baseline run omitted due to frequent request timeouts."
    ax.text(1, -0.15, note,
            transform=ax.transAxes,
            ha='right', va='top',
            fontsize=10, color='gray')
    
    # Save and show
    if save_path:
        plt.savefig(save_path, bbox_inches='tight', dpi=300)

    plt.tight_layout()
    plt.show()
