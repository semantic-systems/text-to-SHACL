import pandas as pd
from typing import List
from resources.schemata.method_schema import var_name_to_fig_label

# Fixed model order
model_order = [
    'meta-llama-3.1-8b-instruct',
    'llama-3.1-sauerkrautlm-70b-instruct',
    'llama-3.3-70b-instruct',
    'mistral-large-instruct',
    'qwen2.5-72b-instruct',
    'qwq-32b',
    'deepseek-r1-distill-llama-70b',
]

def filter_df_by_metrics_and_model(csv_path: str, experiment: str, metrics: List[str]) -> pd.DataFrame:
    """
    Generate a filtered table comparing rows from a specific experiment 
    and selecting only the specified metrics.

    :param csv_path: Path to the CSV file containing the data.
    :param experiment: The experiment name to filter rows by.
    :param metrics: The metrics to filter columns by.
    :return: A filtered DataFrame containing only the specified rows and columns.
    """
    # Load the CSV file into a DataFrame
    df = pd.read_csv(csv_path)

    # Filter rows based on the experiment name (in 'mode' column)
    filtered_df = df[df['mode'] == experiment]

    # Select only the specified columns (metrics) and include 'mode' and 'model'
    selected_columns = ['mode', 'model'] + metrics
    result_df = filtered_df[selected_columns].round(3)

    # Set 'model' as a categorical variable for sorting
    result_df['model'] = pd.Categorical(result_df['model'], categories=model_order, ordered=True)

    # Sort by model order
    result_df = result_df.sort_values('model')

    return result_df

def get_df_for_model_across_modes(csv_path: str, model: str, metrics: List[str]) -> pd.DataFrame:
    """
    Generate a DataFrame comparing the performance of a model across various decoding modes.
    For 'FS' and 'CoT', shows the difference compared to 'BL'.

    :param csv_path: Path to the CSV file.
    :param model: Model name to filter by.
    :param metrics: List of metric column names to include.
    :return: A DataFrame with metrics as rows and modes ('BL', 'FS', 'CoT') as columns.
    """
    df = pd.read_csv(csv_path)

    # Filter for the specified model
    model_df = df[df['model'] == model]

    # Map modes to labels
    mode_mapping = {
        'baseline_0ex0fcv': 'BL',
        'fewshot_1ex3fcv': 'FS',
        'cot_1ex3fcv': 'CoT'
    }
    model_df['mode_label'] = model_df['mode'].map(mode_mapping)

    # Pivot the data so metrics are rows and modes are columns
    final_df = model_df.set_index('mode_label')[metrics].T
    
    final_df.index = [clear_name for var_name, clear_name in var_name_to_fig_label.items() if var_name in metrics]

    # Compute differences for FS and CoT vs BL
    if 'BL' in final_df.columns:
        for col in ['FS', 'CoT']:
            if col in final_df.columns:
                final_df[col] = (final_df[col] - final_df['BL']).round(3)

    return final_df
