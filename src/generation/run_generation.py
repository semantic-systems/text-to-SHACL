"""
run_generation.py

- Given a train directory, test directory, prompt directory, output directory, and mode,
    generate SHACL shapes for all social benefit requirements in train using
    the specified prompting method (mode).
- Save the raw and parsed outputs in the output directory.
- Supported methods: "baseline", "oneshot", "fewshot". # TODO: to be extended
"""

from src.generation.generator_classes.api_access import ChatAIHandler
from src.generation.generator_classes.gen_prompt import PromptComponents, ExampleRetriever
from langchain_openai.chat_models.base import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from typing import Tuple, Dict, Any
import rdflib
import json
import sys
import os


def parse_output(raw_output: str) -> str:
    """Extract parsable Turtle content from model output."""
    if '```turtle' in raw_output and '```' in raw_output:
        start = raw_output.find('```turtle') + len('```turtle')
        end = raw_output.find('```', start)
        data = raw_output[start:end].strip()
    else:
        data = raw_output.strip()
        
    graph = rdflib.Graph()
    try:
        graph.parse(data=data, format="turtle")
        return data
    except Exception:
        return "# No parsable Turtle content found"


def process_file(ontology_path: str, instruction_path: str, test_path: str, train_dir: str, model: ChatOpenAI, mode: str) -> Tuple[str, str]:
    """Generate SHACL shapes for an input file."""
    components = PromptComponents(ontology_path, instruction_path, test_path, train_dir, mode)
    prompt_template = PromptTemplate(
        input_variables=components.input_variables,
        template=components.template,
    )
    prompt = prompt_template.format(
        instruction=components.instruction,
        ontology=components.ontology,
        example=components.examples,
        input=components.requirements,
    )
    
    chain = prompt_template | model
    
    try:
        print(f"Invoking {model.model_name} for {os.path.basename(test_path)}")
        response = chain.invoke({"instruction": components.instruction, "ontology": components.ontology, "input": components.requirements, "example": components.examples})
    # Handle failed requests, in particular timeouts
    except Exception as e:
        print(f"{e}. Mode: {mode}. Model: {model.model_name}. File: {os.path.basename(test_path)}")
        return "", str(e), prompt
    
    return response.content, response.response_metadata, prompt


def save_output(raw_dir: str, parsed_dir: str, prompt: str, prompt_id: str, metadata: Dict[str, Any], response: str, ) -> None:
    """Save raw and parsed outputs."""
    # Ensure directories exist
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(parsed_dir, exist_ok=True)

    # Save raw output
    with open(os.path.join(raw_dir, f"{prompt_id}.json"), "w") as json_file:
        json.dump({"prompt_id": prompt_id, "prompt": prompt, "response_metadata": metadata, "response": response}, json_file, indent=4)
    print(f"Raw output saved to {raw_dir}/{prompt_id}.json")
     
    if response:
        parsed_response = parse_output(response)
        benefit = prompt_id.rsplit("_", 1)[-1]
        with open(os.path.join(parsed_dir, f"{benefit}_gen.ttl"), "w") as json_file:
            json_file.write(parsed_response)
        print(f"Parsed output saved to {parsed_dir}/{benefit}_gen.ttl")

def main(test_dir: str, train_dir: str, prompt_dir: str, output_dir: str, mode: str) -> None:
    """Generate SHACL from social benefit eligibility requirements with specified prompting technique.
    
    :param input_dir: Directory containing input files with eligibility requirements.
    :param prompt_components_dir: Directory containing ontology and instruction files.
    :param model_output_dir: Directory to save the output.
    :param mode: Prompting method used for generating SHACL shapes ('baseline' or 'fewshot').
    
    Side effects:
    - Creates JSON file with final prompt and raw model output in output directory.
    - Creates Turtle file with parsed model output in output directory.
    """
    # Initialize baseline models or main model, depending on mode
    handler = ChatAIHandler()
    custom_configs = {"timeout": 60}
    model_keys = handler.base_models if mode == "baseline" else handler.main_model
    models = [handler.initialize_model(key, custom_configs) for key in model_keys]

    # Set up directories
    ontology_path = os.path.join(prompt_dir, "ontology.ttl")
    instruction_path = os.path.join(prompt_dir, f"instructions/instruction_{mode}.txt")
    raw_dir = os.path.join(output_dir, "raw_output")
    parsed_dir = os.path.join(output_dir, mode)

    # Process each input file with each model
    for model in models:
        model_parsed_dir = os.path.join(parsed_dir, model.model_name)
        for test_file in os.listdir(test_dir):
            test_path = os.path.join(test_dir, test_file)
            prompt_id = f"{mode}_{model.model_name}_{test_file.split('_')[0]}"
            response, metadata, prompt = process_file(ontology_path, instruction_path, test_path, train_dir, model, mode)
            save_output(raw_dir, model_parsed_dir, prompt, prompt_id, metadata, response)

if __name__ == "__main__":
    if len(sys.argv) != 6:
        print("Usage: python run_generation.py <test_dir> <train_dir> <prompt_dir> <output_dir> <mode>")
        sys.exit(1)
    
    test_dir = sys.argv[1]
    train_dir = sys.argv[2]
    prompt_dir = sys.argv[3]
    output_dir = sys.argv[4]
    mode = sys.argv[5]  # 'baseline' or 'oneshot' or 'fewshot'

    print(f"Starting generation for mode: {mode}")
    main(test_dir, train_dir, prompt_dir, output_dir, mode)