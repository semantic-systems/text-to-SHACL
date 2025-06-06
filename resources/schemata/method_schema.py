"""  
method_schema.py

Information about the methodology including:
- supported_modes: Dictionary of supported modes with their descriptions,
    synonyms, models, and prompt variables.
- avg_syntax_metrics, avg_all_metrics, and avg_valid_only_metrics: Lists
    of metric names used for evaluation
- metric_to_legend: Dictionary mapping full metric names to shortcuts, for
    use in plots and legends.
"""

supported_modes = {
    "baseline": {
        "description": "Prompt includes instruction + ontology + input, no examples.",
        "synonyms": ["zeroshot", "base"],
        "prompt_variables": ["instruction", "ontology", "input"]
    },
    "fewshot": {
        "description": "Prompt includes instruction + ontology + example input-output pairs + input.",
        "synonyms": ["incontext learning", "in-context learning", "incontext", "few-shot", "fs"],
        "prompt_variables": ["instruction", "ontology", "fewshot_examples", "input"]
    },
    "cot": {
        "description": "Prompt includes instruction + ontology + example input-output pairs with step-by-step solution + input.",
        "synonyms": ["chain of thought", "chain-of-thought"],
        "prompt_variables": ["instruction", "ontology", "cot_examples", "input"]
    }
}

syntax_metrics = ["valid_turtle_all", "valid_shacl_all"]

metrics_all_mean_std = [
    "graph_edit_distance_all",
    "gbert_f1_all",
    "triple_f1_all", 
    "triple_precision_all",
    "triple_recall_all",
    "validation_f1_all",
    "validation_precision_all",
    "validation_recall_all",
    "validation_accuracy_all",
]

metrics_all_mean_std = [
    "graph_edit_distance_all_mean",
    "graph_edit_distance_all_std",
    "gbert_f1_all_mean",
    "gbert_f1_all_std",
    "triple_f1_all_mean", 
    "triple_f1_all_std", 
    "triple_precision_all_mean",
    "triple_precision_all_std",
    "triple_recall_all_mean",
    "triple_recall_all_std",
    "validation_f1_all_mean",
    "validation_f1_all_std",
    "validation_precision_all_mean",
    "validation_precision_all_std",
    "validation_recall_all_mean",
    "validation_recall_all_std",
    "validation_accuracy_all_mean",
    "validation_accuracy_all_std",
]


metrics_valid_mean_std = [
    "graph_edit_distance_valid_only_mean",
    "graph_edit_distance_valid_only_std",
    "gbert_f1_valid_only_mean",
    "gbert_f1_valid_only_std",
    "triple_f1_valid_only_mean", 
    "triple_f1_valid_only_std", 
    "triple_precision_valid_only_mean",
    "triple_precision_valid_only_std",
    "triple_recall_valid_only_mean",
    "triple_recall_valid_only_std",
    "validation_f1_valid_only_mean",
    "validation_f1_valid_only_std",
    "validation_precision_valid_only_mean",
    "validation_precision_valid_only_std",
    "validation_recall_valid_only_mean",
    "validation_recall_valid_only_std",
    "validation_accuracy_valid_only_mean",
    "validation_accuracy_valid_only_std",
]

gm_metrics_valid = [
    "graph_edit_distance_valid_only",
    "gbert_f1_valid_only",
    "triple_f1_valid_only", 
    "triple_precision_valid_only",
    "triple_recall_valid_only",
    "validation_f1_valid_only",
    "validation_precision_valid_only",
    "validation_recall_valid_only",
    "validation_accuracy_valid_only",
]

metric_to_legend = {
    # Graph Edit Distance
    "graph_edit_distance_all": "GED",
    "graph_edit_distance_valid_only": "GED",
    "graph_edit_distance_all_mean": "GED",
    "graph_edit_distance_all_std": "GED SD",
    "graph_edit_distance_valid_only_mean": "GED",
    "graph_edit_distance_valid_only_std": "GED SD",
    
    # GBERT
    "gbert_f1_all": "GBERT F1",
    "gbert_precision_all": "GBERT Precision",
    "gbert_recall_all": "GBERT Recall",
    "gbert_f1_valid_only": "GBERT F1",
    "gbert_precision_valid_only": "GBERT Precision",
    "gbert_recall_valid_only": "GBERT Recall",
    "gbert_f1_all_mean": "GBERT F1",
    "gbert_f1_all_std": "GBERT F1 SD",
    "gbert_f1_valid_only_mean": "GBERT F1",
    "gbert_f1_valid_only_std": "GBERT F1 SD",
    "gbert_precision_all_mean": "GBERT Precision",
    "gbert_precision_all_std": "GBERT Precision SD",
    "gbert_precision_valid_only_mean": "GBERT Precision",
    "gbert_precision_valid_only_std": "GBERT Precision SD",
    "gbert_recall_all_mean": "GBERT Recall",
    "gbert_recall_all_std": "GBERT Recall SD",
    "gbert_recall_valid_only_mean": "GBERT Recall",
    "gbert_recall_valid_only_std": "GBERT Recall SD",
    
    # Triple Matching
    "triple_f1_all": "Triple F1",
    "triple_precision_all": "Triple Precision",
    "triple_recall_all": "Triple Recall",
    "triple_accuracy_all": "Triple Accuracy",
    "triple_f1_valid_only": "Triple F1",
    "triple_precision_valid_only": "Triple Precision",
    "triple_recall_valid_only": "Triple Recall",
    "triple_accuracy_valid_only": "Triple Accuracy",
    "triple_f1_all_mean": "Triple F1",
    "triple_f1_all_std": "Triple F1 SD",
    "triple_f1_valid_only_mean": "Triple F1",
    "triple_f1_valid_only_std": "Triple F1 SD",
    "triple_precision_all_mean": "Triple Precision",
    "triple_precision_all_std": "Triple Precision SD",
    "triple_precision_valid_only_mean": "Triple Precision",
    "triple_precision_valid_only_std": "Triple Precision SD",
    "triple_recall_all_mean": "Triple Recall",
    "triple_recall_all_std": "Triple Recall SD",
    "triple_recall_valid_only_mean": "Triple Recall",
    "triple_recall_valid_only_std": "Triple Recall SD",
    "triple_accuracy_all_mean": "Triple Accuracy",
    "triple_accuracy_all_std": "Triple Accuracy SD",
    "triple_accuracy_valid_only_mean": "Triple Accuracy",
    "triple_accuracy_valid_only_std": "Triple Accuracy SD",
    
    # Validation
    "validation_f1_all": "Validation F1",
    "validation_precision_all": "Validation Precision",
    "validation_recall_all": "Validation Recall",
    "validation_accuracy_all": "Validation Accuracy",
    "validation_f1_valid_only": "Validation F1",
    "validation_precision_valid_only": "Validation Precision",
    "validation_recall_valid_only": "Validation Recall",
    "validation_accuracy_valid_only": "Validation Accuracy",
    "validation_f1_all_mean": "Validation F1",
    "validation_f1_all_std": "Validation F1 SD",
    "validation_f1_valid_only_mean": "Validation F1",
    "validation_f1_valid_only_std": "Validation F1 SD",
    "validation_precision_all_mean": "Validation Precision",
    "validation_precision_all_std": "Validation Precision SD",
    "validation_precision_valid_only_mean": "Validation Precision",
    "validation_precision_valid_only_std": "Validation Precision SD",
    "validation_recall_all_mean": "Validation Recall",
    "validation_recall_all_std": "Validation Recall SD",
    "validation_recall_valid_only_mean": "Validation Recall",
    "validation_recall_valid_only_std": "Validation Recall SD",
    "validation_accuracy_all_mean": "Validation Accuracy",
    "validation_accuracy_all_std": "Validation Accuracy SD",
    "validation_accuracy_valid_only_mean": "Validation Accuracy",
    "validation_accuracy_valid_only_std": "Validation Accuracy SD",
    
    # Syntax
    "valid_turtle_all": "Turtle",
    "valid_shacl_all": "SHACL",
    "valid_turtle_all_mean": "Turtle",
    "valid_turtle_all_std": "Turtle SD",
    
    "conversion_rate": "Conversion Rate",
    
    "ged_timeout_all": "GED Timeout",
}

models_to_legend = {
    "meta-llama-3.1-8b-instruct": "Llama 8b",
    "qwq-32b": "QwQ",
    "deepseek-r1-distill-llama-70b": "DeepSeek",
    "llama-3.3-70b-instruct": "LLama 70b",
    "llama-3.1-sauerkrautlm-70b-instruct": "Sauerkraut",
    "mistral-large-instruct": "Mistral",
    "qwen2.5-72b-instruct": "Qwen"
}

modes_to_legend = {
    'baseline_0ex0fcv': 'Base',
    'fewshot_1ex3fcv': 'FS',
    'cot_1ex3fcv': 'CoT'
}
