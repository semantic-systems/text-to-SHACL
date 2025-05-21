""" 
AnalyzeSyntaxErrors.py

Functions for analyzing the validation results produced when validating SHACL 
graphs against the SHACL Meta shapes graph, which encodes SHACL syntax rules:
- ratio of SHACL graphs with syntax errors
- average number of validation results per ill-formed SHACL output
- distribution of source shapes and validation result messages
- visualization in a heatmap
"""

import re
import os
import json
import textwrap
import seaborn as sns
import matplotlib.pyplot as plt
import pandas as pd
from collections import defaultdict
from rdflib import Graph
from pyshacl import validate
from pyshacl.errors import ReportableRuntimeError
from typing import Dict, List, Tuple, Any
from matplotlib.patches import Patch

def extract_source_shapes_and_messages_without_details(validation_report: str) -> Tuple[List[str], List[str]]:
    """
    Extracts source shapes and messages from a SHACL validation report, 
    excluding any content found within "Details:" blocks.

    :param validation_report: The raw SHACL validation report as a string.
    :return: A tuple containing two lists: source shapes and messages.
    """
    lines = validation_report.splitlines()
    results = []
    current_result = {}
    in_details_block = False

    for line in lines:
        stripped = line.strip()

        # Start or end of a details block
        if stripped.startswith("Details:"):
            in_details_block = True
            continue
        elif in_details_block:
            # If indentation is less than "Details:" sub-block, flag exit
            if not line.startswith("\t") and not line.startswith(" " * 4):
                in_details_block = False
            # Otherwise, we are still in the details block
            else:
                continue

        if not in_details_block:
            if stripped.startswith("Source Shape:"):
                current_result["source_shape"] = stripped.replace("Source Shape:", "").strip()
            elif stripped.startswith("Message:"):
                current_result["message"] = stripped.replace("Message:", "").strip()
                results.append(current_result)
                current_result = {}
    
    return results

def get_meta_shapes_validation_report(shacl_path: str) -> Dict[str, Any]:
    """ 
    Validates a SHACL file against the meta shapes graph using pySHACL.

    :param shacl_path: Path to the SHACL file to be validated.
    :return: A dictionary containing the validation results.
    """
    syntax_error_msg = (
        "SHACL File does not validate against the "
        "SHACL Shapes SHACL (MetaSHACL) file."
    )
    min_rdf_graph = (
        "@prefix ex: <http://example.org/> .\n"
        "ex:Subject ex:hasProperty 'object' ."
    )

    data_graph = Graph()
    data_graph.parse(data=min_rdf_graph, format="turtle")
    shacl_graph = Graph()
    shacl_graph.parse(shacl_path, format="turtle")

    # Set default results
    result = {
        "path": shacl_path,
        "valid_shacl": 0,
        "syntax_error": 0,
        "unexpected_error": 0,
        "validation_report": None,
        "nof_validation_results": None,
        "validation_results": None
    }

    try:
        validate(
            data_graph=data_graph,
            shacl_graph=shacl_graph,
            debug=False,
            meta_shacl=True
        )
        # If validation passes without exception, it's a valid SHACL
        result["valid_shacl"] = 1

    except ReportableRuntimeError as e:
        if syntax_error_msg in e.message:
            result["syntax_error"] = 1
            report = str(e)
            result["validation_report"] = report

            # Extract number of validation results
            match_results = re.search(r"Results\s*\((\d+)\):", report)
            if match_results:
                result["nof_validation_results"] = int(match_results.group(1))

            result["validation_results"] = extract_source_shapes_and_messages_without_details(report)

        else:
            result["unexpected_error"] = 1
            result["validation_report"] = str(e)

    except Exception as e:
        result["unexpected_error"] = 1
        result["validation_report"] = str(e)

    return result

def analyze_all_runs(results_dir: str, save_path: str = None) -> List[Dict[str,Any]]:
    """
    Analyzes the meta shapes graph validation results for SHACL files in all 
    experiment runs and returns all results.

    :param results_dir: Path to the top-level results directory.
    :param save_path: Path to optionally save the analysis results.
    :return: A dictionary with validation results for each SHACL file.
    """
    results = []

    for run in os.listdir(results_dir):
        run_path = os.path.join(results_dir, run)
        if not os.path.isdir(run_path):
            continue

        for model in os.listdir(run_path):
            model_path = os.path.join(run_path, model)
            if not os.path.isdir(model_path):
                continue

            parsed_output_dir = os.path.join(model_path, "output", "parsed_output")
            if not os.path.exists(parsed_output_dir) or len(os.listdir(parsed_output_dir)) == 0:
                print(f"Warning: No parsed output found for {model_path}")
                continue

            for file in os.listdir(parsed_output_dir):
                if not file.endswith(".ttl"):
                    continue
                
                # Metadata
                file_result = {
                    "experiment": run,
                    "prompt": run.split("_")[0],
                    "model": model,
                    "file": file
                }
                
                # Get validation results
                file_path = os.path.join(parsed_output_dir, file)
                valiadtion_result = get_meta_shapes_validation_report(file_path)
                file_result.update(valiadtion_result)
                
                # Append file results to list of all results
                results.append(file_result)
    
    # Optionally save the results to a JSON file
    if save_path:
        with open(save_path, 'w') as f:
            json.dump(results, f, indent=4)
        print(f"Results saved to {save_path}")

    return results

def get_unique_source_nodes_and_msgs(json_path: str) -> Dict[str, Any]:
    """
    Analyzes occurrences of messages ad source nodes in validaiton reports.

    :param json_path: Path to the JSON file containing the validation results.
    :return: Dictionary with information on unique source nodes, messages, and
                source-node-message pairs.
    """
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    source_nodes = set()
    messages = set()
    source_message_pairs = set()

    for item in data:
        validation_results = item.get('validation_results')

        # Skip if validation_results is None
        if validation_results is None:
            continue

        for result in validation_results:
            source = result.get('source_shape')
            message = result.get('message')

            if source and message:
                source_nodes.add(source)
                messages.add(message)
                source_message_pairs.add((source, message))

    return {
        "unique_source_nodes": source_nodes,
        "source_node_count": len(source_nodes),
        "unique_messages": messages,
        "message_count": len(messages),
        "unique_source_message_pairs": source_message_pairs,
        "source_message_pair_count": len(source_message_pairs),
    }

def compute_avg_nof_validation_results(json_path: str) -> pd.DataFrame:
    """ 
    Computes the average number of validation results per ill-formed SHACL output,
    macro averaged over three runs for each (prompt, model) pair.
    
    :param json_path: Path to the JSON file containing the validation results.
    :return: DataFrame with the average values.
    """
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Group entries by (prompt, model, run_id)
    grouped = defaultdict(list)
    for entry in data:
        prompt = entry["prompt"]
        model = entry["model"]
        experiment = entry["experiment"]
        run_id = experiment.split('_')[-1]
        key = (prompt, model, run_id)
        grouped[key].append(entry)

    # For each (prompt, model), collect run-level averages
    results = defaultdict(list)
    for (prompt, model, run_id), entries in grouped.items():
        # Filter for files with syntax errors
        syntax_error_files = [e for e in entries if e.get("syntax_error", 0) > 0]
        if not syntax_error_files:
            continue
        total_validation_results = 0
        for e in syntax_error_files:
            num_results = e.get("nof_validation_results", 0)
            total_validation_results += num_results
        avg_validation_results = total_validation_results / len(syntax_error_files)
        results[(prompt, model)].append(avg_validation_results)

    # Compute macro average across 3 runs for each (prompt, model)
    final_data = []
    for (prompt, model), run_averages in results.items():
        macro_avg = sum(run_averages) / len(run_averages)
        final_data.append({
            "Prompt": prompt,
            "Model": model,
            "Average number of validation results per ill-formed SHACL output": round(macro_avg, 3)
        })

    return pd.DataFrame(final_data)

def extract_shape_messages_from_file(json_path: str, prompts: List[str], save_path: str = None) -> List[Dict]: 
    """
    Extracts unique validation error messages grouped by source shape for syntax error 
    outputs filtered by prompt.

    :param json_path: Path to a JSON file containing entries with validation results.
    :param prompt_filter: Prompts by which to filter the entries of interest.
    :return: A dictionary mapping each source shape to a sorted list of associated 
                unique validation error messages.
    """
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    shape_to_messages = defaultdict(set)

    filtered = [entry for entry in data if entry['prompt'] in prompts and entry.get('syntax_error', 0) == 1]
    
    for item in filtered:
        validation_result = item.get("validation_results", [])
        
        for result in validation_result:
            source_shape = result.get("source_shape")
            message = result.get("message")
            if source_shape and message:
                shape_to_messages[source_shape].add(message)
    
    df = {shape: sorted(messages) for shape, messages in shape_to_messages.items()}
    
    if save_path:
        with open(save_path, "w", encoding="utf-8") as f:
            json.dump(df, f, indent=4, ensure_ascii=False)
    
    # Convert sets to sorted lists for consistency
    return df

def get_distribution_of_source_shapes(json_path: str, prompts: List[str]) -> pd.DataFrame:
    """
    Computes the distribution of source shape occurrences for syntax error outputs across models, filtered by prompt.

    :param json_path: Path to a JSON file containing model output entries with validation results.
    :param prompts: A list of prompt strings to filter the entries of interest.
    :return: A pandas DataFrame where each row corresponds to a unique source shape and each column to a model,
             with values representing the normalized frequency of that source shape among syntax error outputs.
    """
    with open(json_path, 'r') as f:
        data = json.load(f)

    # Filter data for selected prompts and outputs with syntax errors
    filtered = [entry for entry in data if entry['prompt'] in prompts and entry.get('syntax_error', 0) == 1]

    # Prepare aggregation structures
    unique_source_shape_counts = defaultdict(lambda: defaultdict(int))  # error_counts[error_type][model] = count
    total_source_shapes_per_model = defaultdict(int)  # total_errors_per_model[model] = count

    # Parse validation reports and aggregate
    for entry in filtered:
        model = entry['model']
        source_shapes = [result["source_shape"] for result in entry["validation_results"]]

        for shape in source_shapes:
            unique_source_shape_counts[shape][model] += 1
            total_source_shapes_per_model[model] += 1

    # Create DataFrame with averages
    all_unique_source_shapes = sorted(unique_source_shape_counts.keys())
    all_models = sorted(total_source_shapes_per_model.keys())

    data_matrix = []
    for shape in all_unique_source_shapes:
        row = []
        for model in all_models:
            total = total_source_shapes_per_model[model]
            count = unique_source_shape_counts[shape].get(model, 0)
            average = count / total if total else 0
            row.append(average)
        data_matrix.append(row)

    df = pd.DataFrame(data_matrix, index=all_unique_source_shapes, columns=all_models)
    df.index.name = "source_shape"
    return df

def plot_source_shape_distribution_heatmap(json_path: str, prompts: List[str], save_path: str = None) -> None:
    """
    Generates a heatmap showing the distribution of source shapes across models,
    with abbreviated x-axis labels and a legend mapping them to full identifiers.
    Optionally saves the plot to a specified path.

    :param json_path: Path to a JSON file containing model output entries with validation results.
    :param prompt_filter: A list of prompt strings to filter the entries of interest.
    :param save_path: Optional path to save the plot.
    """
    # Get distribution of source shapes
    df = get_distribution_of_source_shapes(json_path, prompts)

    # Order df from most to least frequent source shape
    row_sums = df.sum(axis=1)
    source_shape_order = row_sums.sort_values(ascending=False).index
    df_ordered = df.loc[source_shape_order]
    
    # Plot shapes on the x axis and models on the y axis
    df_plot = df_ordered.transpose()

    # Generate short labels for x-ticks
    n = df_plot.shape[1]
    xticklabels_short = [f"E{i:02d}" for i in range(1, n + 1)]
    xticklabels_og = list(df_plot.columns)
    df_plot.columns = xticklabels_short

    plt.figure(figsize=(12, 10))
    ax = sns.heatmap(
        df_plot,
        annot=False,
        cmap="Blues",
        linewidths=0.5,
    )

    # Set axes labels and ticks
    ax.set_xticklabels(xticklabels_short, rotation=45, ha='right')
    ax.set_yticklabels(ax.get_yticklabels(), rotation=0)

    # Create legend for x-tick-labels
    plt.subplots_adjust(bottom=0.5)
    legend_handles = [
        Patch(
            facecolor='none', edgecolor='none',
            label=rf"$\bf{{{e}}}$: {textwrap.fill(orig, 145)}"
        )
        for e, orig in zip(xticklabels_short, xticklabels_og)
    ]
    
    leg = ax.legend(
        handles=legend_handles,
        title="Source Shape Mapping",
        loc='lower left',
        bbox_to_anchor=(0., -0.7),
        ncol=1,
        frameon=False,
        fontsize="small",
        title_fontsize="medium",
        handlelength=0,
        alignment="left",
    )
    leg.get_title().set_fontweight('bold')

    plt.tight_layout()
    
    # Save if specified
    if save_path:
        plt.savefig(save_path)
        print(f"Plot saved to {save_path}")
        
    plt.show()