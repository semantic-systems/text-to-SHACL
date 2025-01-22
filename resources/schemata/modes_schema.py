"""  
modes_schema.py

Information about supported modes for inference.
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
        "prompt_variables": ["instruction", "ontology", "examples"]
    }
}