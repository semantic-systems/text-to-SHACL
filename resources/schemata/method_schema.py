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

avg_syntax_metrics = ['valid_turtle_all', 'valid_shacl_all']

avg_all_metrics = [
    'graph_edit_distance_all', 'gbert_f1_all', 'triple_f1_all', 'validation_f1_all', 
]

avg_valid_only_metrics = [
    'graph_edit_distance_valid_only', 'gbert_f1_valid_only', 'triple_f1_valid_only', 
    'validation_f1_valid_only'
]

metric_to_legend = {
    "graph_edit_distance_all": "GED",
    "graph_edit_distance_valid_only": "GED",
    "gbert_f1_all": "GBERT F1",
    "gbert_f1_valid_only": "GBERT F1",
    "triple_f1_all": "Triple F1",
    "triple_f1_valid_only": "Triple F1",
    "validation_f1_all": "Validation F1",
    "validation_f1_valid_only": "Validation F1",
    "valid_turtle_all": "Valid Turtle",
    "valid_shacl_all": "Valid SHACL",
}