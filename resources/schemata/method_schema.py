"""  
method_schema.py

Information about the methodology including:
- supported_modes: Dictionary of supported modes with their descriptions,
    synonyms, models, and prompt variables.

"""

supported_modes = {
    "baseline": {
        "description": "Prompt includes instruction + ontology, inference is executed with multiple models.",
        "synonyms": ["zeroshot", "base"],
        "models": ['meta-llama-3.1-8b-instruct', 'llama-3.1-nemotron-70b-instruct', 'llama-3.1-sauerkrautlm-70b-instruct', 'mistral-large-instruct', 'qwen2.5-72b-instruct'],
        "prompt_variables": ["instruction", "ontology"]
    },
    "fewshot": {
        "description": "Prompt includes instruction + ontology + variable number of randomly selected examples from train split, inference is executed with main model only.",
        "synonyms": ["incontext learning", "in-context learning", "incontext", "few-shot"],
        "models": ['mistral-large-instruct'],
        "prompt_variables": ["instruction", "ontology", "fewshot_examples"]
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