"""
run_generation.py

- Given a train directory, test directory, prompt directory, output directory, and mode,
    generate SHACL shapes for all social benefit requirements in train using
    the specified prompting method (mode).
- Save the raw and parsed outputs in the output directory.
- Supported methods: "baseline", "oneshot", "fewshot". # TODO: to be extended
"""

from src.generation.generator_classes.api_access import ChatAIHandler
from src.generation.generator_classes.prompt_template import PromptComponents
from langchain_openai.chat_models.base import ChatOpenAI
from langchain_core.prompts import PromptTemplate
from typing import Tuple, Dict, Any
from datetime import datetime
import rdflib
import argparse
import json
import sys
import os


def parse_output(raw_output: str) -> str:
    """Extract parsable Turtle content from model output."""
    # Extract Turtle content, if it is explicitly marked
    if '```turtle' in raw_output and '```' in raw_output:
        start = raw_output.find('```turtle') + len('```turtle')
        end = raw_output.find('```', start)
        data = raw_output[start:end].strip()
    else:
        data = raw_output.strip()
    
    # If data is not parsable, return empty string
    graph = rdflib.Graph()
    try:
        graph.parse(data=data, format="turtle")
        return data
    except Exception as e:
        return ""


def process_file(ontology_path: str, instruction_path: str, test_path: str, train_dir: str, model: ChatOpenAI, mode: str) -> Tuple[str, str]:
    """Generate SHACL shapes for an input file using the specified model and prompting mode."""
    components = PromptComponents(ontology_path, instruction_path, test_path, train_dir, mode)
    prompt_template = PromptTemplate(
        input_variables=components.input_variables,
        template=components.template,
    )
    prompt = prompt_template.format(
        instruction=components.instruction,
        ontology=components.ontology,
        example=components.examples.examples_string,
        input=components.requirements,
    )
    
    chain = prompt_template | model
    
    try:
        print(f"Invoking chain...")
        response = chain.invoke({"instruction": components.instruction, "ontology": components.ontology, "input": components.requirements, "example": components.examples})
        # Add timestamp and selected examples to response metadata
        response.response_metadata["timestamp"] = datetime.now().isoformat(timespec='seconds')
        response.response_metadata["examples"] = components.examples.examples_list
    # Set output manually if an error occurs during generation
    except Exception as e:
        print(f"Exception: {e}")
        return "", str(e), prompt
    
    return response.content, response.response_metadata, prompt


def save_output(raw_dir: str, parsed_dir: str, prompt: str, prompt_id: str, metadata: Dict[str, Any], response: str) -> None:
    """Save raw and parsed model outputs."""
    # Ensure directories exist
    os.makedirs(raw_dir, exist_ok=True)
    os.makedirs(parsed_dir, exist_ok=True)

    # Save raw output
    raw_output_path = os.path.join(os.path.join(raw_dir, f"{prompt_id}.json"))
    with open(raw_output_path, "w", encoding="utf-8") as json_file:
        json.dump({"prompt_id": prompt_id, "prompt": prompt, "response_metadata": metadata, "response": response}, 
                  json_file, indent=4, ensure_ascii=False,)
    print(f"Raw output saved to {raw_output_path}")
    
    # Save parsed output 
    if response:
        parsed_response = parse_output(response)
        parsed_output_path = os.path.join(parsed_dir, f"{prompt_id}.ttl")
        #benefit = prompt_id.rsplit("_", 1)[-1]
        with open(os.path.join(parsed_output_path), "w", encoding="utf-8") as json_file:
            json_file.write(parsed_response)
        print(f"Parsed output saved to {parsed_output_path}")

def main(test_dir: str, train_dir: str, prompt_dir: str, output_dir: str, mode: str) -> None:
    """Generate SHACL from social benefit eligibility requirements with specified prompting technique.
    
    :param test_dir: Directory with benefit descriptions used for testing.
    :param train_dir: Directory with benefit descriptions used as examples during prompting.
    :param prompt_components_dir: Directory containing ontology and instruction files.
    :param model_output_dir: Directory to save the output.
    :param mode: Prompting method used for generating SHACL shapes ('baseline' or 'fewshot').
    
    Side effects:
    - Creates JSON file with final prompt and raw model output in output directory.
    - Creates Turtle file with parsed model output in output directory.
    """
    # Initialize baseline models or main model, depending on mode
    handler = ChatAIHandler()
    
    model_keys = handler.base_models if mode == "baseline" else handler.main_model
    models = [handler.initialize_model(key) for key in model_keys]

    # Get paths to prompt components
    ontology_path = os.path.join(prompt_dir, "ontology.ttl")
    instruction_path = os.path.join(prompt_dir, f"instructions/instruction_{mode}.txt")
    
    # Ensure prompt components exist
    if not os.path.exists(ontology_path):
        raise FileNotFoundError(f"Ontology not found: {ontology_path}")
    if not os.path.exists(instruction_path):
        raise FileNotFoundError(f"Instruction file not found: {instruction_path}")
    
    # Set up directories for raw and parsed output
    raw_dir = os.path.join(output_dir, "raw_output", mode)
    parsed_dir = os.path.join(output_dir, mode)

    # Generate SHACL shapes for each test file with each model
    for model_index, model in enumerate(models):
        # If more than one model is used, create separate output directories
        model_parsed_dir = parsed_dir if len(models) == 1 else os.path.join(parsed_dir, model.model_name)
        for file_index, test_file in enumerate(os.listdir(test_dir)):
            print(f"Processing {os.path.basename(test_file)} (File {file_index+1}/{len(os.listdir(test_dir))}) " +
                  f"with {model.model_name} (Model {model_index+1}/{len(models)})")
            test_path = os.path.join(test_dir, test_file)
            prompt_id = f"{mode}_{model.model_name}_{test_file.split('_')[0]}"
            response, metadata, prompt = process_file(ontology_path, instruction_path, test_path, train_dir, model, mode)
            save_output(raw_dir, model_parsed_dir, prompt, prompt_id, metadata, response)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate SHACL shapes from benefit descriptions using the specified prompting method.")

    parser.add_argument("test_dir", help="Directory with benefit descriptions used for testing.")
    parser.add_argument("train_dir", help="Directory with benefit descriptions used as examples during prompting.")
    parser.add_argument("prompt_components_dir", help="Directory containing ontology and instruction files.")
    parser.add_argument("model_output_dir", help="Directory to save the output.")
    parser.add_argument("mode", choices=["baseline", "oneshot", "fewshot"], help="Prompting method used for generating SHACL shapes ('baseline' or 'fewshot').")

    args = parser.parse_args()

    main(args.test_dir, args.train_dir, args.prompt_components_dir, args.model_output_dir, args.mode)