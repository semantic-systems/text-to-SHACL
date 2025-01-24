""" 
RunInference.py

- Use LLM-inference to generate SHACL shapes for social benefits in the test split.
- Save raw and parsed outputs in the results directory for this method.
- Currently supported methods: 
    - "baseline": Prompt includes instruction + ontology, inference is executed 
    with multiple models.
    - "xshotrandom": Prompt includes instruction + ontology + variable number
    of randomly selected examples from train split, inference is executed with main
    model only.
    # TODO: to be extended
"""

import os
import json
import argparse
import rdflib
import shutil
from typing import Optional
from datetime import datetime
from .Model import ModelHandler
from .Prompt import PromptHandler
from Utils.Logger import setup_logger
from resources.schemata.modes_schema import supported_modes

logger = setup_logger(__name__, "logs/RunInference.log")

def retrieve_parsable_turtle(raw_output: str) -> Optional[str]:
    """Return parsable Turtle content from model output, if any."""
    prefixes = ["@prefix", "@base", "<http://", "PREFIX"]
    
    # If Turtle flags are present, extract everything in between
    if '```turtle' in raw_output and '```' in raw_output:
        start = raw_output.find('```turtle') + len('```turtle')
        end = raw_output.find('```', start)
        turtle_candidate = raw_output[start:end].strip()
    # If a prefix is present, extract everything after the first occurrence
    elif any(opener in raw_output for opener in prefixes):
        start = raw_output.find(next(term for term in prefixes if term in raw_output))
        turtle_candidate = raw_output[start:].strip()
    else:
        turtle_candidate = raw_output.strip()
    
    # Check if the data is parsable
    graph = rdflib.Graph()
    try:
        graph.parse(data=turtle_candidate, format="turtle")
    except Exception as e:
        logger.warning(f"Turtle candidate not parsable: {e}")
        return None

    return turtle_candidate

def run_fewshot_experiment(test_dir: str, prompt_components_dir: str, model_handler: ModelHandler, results_dir: str, train_dir: str, examples: int, mode: str = "fewshot"):
    logger.info(f"Starting {mode} experiment...")
    
    # Initialize instance of main model
    model = model_handler.initialize_model(model_handler.main_model)
    
    # Clear experiment directory if it already exists
    experiment_dir = os.path.join(results_dir, mode)
    if os.path.exists(experiment_dir):
        shutil.rmtree(experiment_dir)
        logger.info(f"Cleared directory for {mode} experiment.")
    
    results = {}
    parsed_output_dir = os.path.join(experiment_dir, "output", "parsed_output")
    os.makedirs(parsed_output_dir, exist_ok=True)
    for test_file in os.listdir(test_dir):
        run_key = f"{mode}_{model.model_name}_{test_file}"
        parsed_output_path = os.path.join(parsed_output_dir, f"{run_key}.ttl")
        
        # Contruct prompt
        prompt_handler = PromptHandler(mode=mode, input_path=os.path.join(test_dir, test_file), prompt_components_dir=prompt_components_dir, num_examples=examples, train_dir=train_dir)
        prompt = prompt_handler.prompt_template
        prompt_components = prompt_handler.prompt_components
        chain = prompt | model
        
        # Invoke model
        logger.info(f"Invoking {model.model_name}")
        start_time = datetime.now()
        try:
            response = chain.invoke(prompt_components)
        except Exception as e:
            logger.error(f"Error invoking {model.model_name}: {e}")
            continue
        end_time = datetime.now()
        
        # Try to retrieve valid Turtle from raw output
        raw_output = response.content
        turtle_output = retrieve_parsable_turtle(raw_output)
        
        # Save parsed output if it includes valid Turtle
        if turtle_output is not None:
            try:
                with open(parsed_output_path, "w", encoding="utf-8") as turtle_file:
                    turtle_file.write(turtle_output)
                logger.info(f"Saved parsed output to {parsed_output_path}")
            except Exception as e:
                logger.error(f"Error saving parsed output: {e}")
            
        # Fetch metadata, rendered prompt, and raw response
        metadata = {
            "mode": mode,
            "model": model.model_name,
            "valid_turtle": False if turtle_output is None else True,
            "test_file": test_file,
            "in-context examples": prompt_handler.examples,
            "timestamp": start_time.isoformat(),
            "runtime": (end_time - start_time).total_seconds(),
            "parsed_output_path": None if turtle_output is None else parsed_output_path,
            "token_usage": response.response_metadata["token_usage"],
            "finish_reason": response.response_metadata["finish_reason"]
        }
        results[run_key] = {
            "metadata": metadata,
            "rendered_prompt": prompt_handler.rendered_prompt,
            "raw_response": response.content,
        }
    
    # Save raw outputs
    raw_output_path = os.path.join(experiment_dir, "output", f"{mode}_{model.model_name}_raw_output.json")
    with open(raw_output_path, 'w', encoding='utf-8') as json_file:
        json.dump(results, json_file, ensure_ascii=False, indent=4)
    logger.info(f"Saved raw outputs to {raw_output_path}")
        
    logger.info(f"{mode.capitalize()} experiment completed!")

def run_baseline_experiment(test_dir: str, prompt_components_dir: str, model_handler: ModelHandler, results_dir: str, mode: str = "baseline"):
    """
    Run the baseline experiment, i.e. zeroshot prompting with multiple models.
    Invokes each base model on each test file and saves the raw and parsed outputs.

    :param test_dir: Directory containing test files.
    :param prompt_components_dir: Directory with components for constructing prompts.
    :param model_handler: Handler for initializing and managing model instances.
    :param results_dir: Directory to save the experiment results.
    :param mode: Mode of the experiment (default: "baseline").
    """
    logger.info(f"Starting {mode} experiment...")
    
    # Initialize model instances
    models = [model_handler.initialize_model(key) for key in model_handler.base_models]
    logger.info(f"Succesfully initialized base models: {', '.join([model.model_name for model in models])}")
    
    # Clear experiment directory if it already exists
    experiment_dir = os.path.join(results_dir, mode)
    if os.path.exists(experiment_dir):
        shutil.rmtree(experiment_dir)
        logger.info(f"Cleared directory for {mode} experiment.")
    
    for model in models:
        results = {}
        parsed_output_dir = os.path.join(experiment_dir, model.model_name, "output", "parsed_output")
        os.makedirs(parsed_output_dir, exist_ok=True)
        for test_file in os.listdir(test_dir):
            run_key = f"{mode}_{model.model_name}_{test_file}"
            parsed_output_path = os.path.join(parsed_output_dir, f"{run_key}.ttl")
            
            # Contruct prompt
            prompt_handler = PromptHandler(mode=mode, input_path=os.path.join(test_dir, test_file), prompt_components_dir=prompt_components_dir)
            prompt = prompt_handler.prompt_template
            prompt_components = prompt_handler.prompt_components
            chain = prompt | model
            
            # Invoke model
            logger.info(f"Invoking {model.model_name}")
            start_time = datetime.now()
            try:
                response = chain.invoke(prompt_components)
            except Exception as e:
                logger.error(f"Error invoking {model.model_name}: {e}")
                continue
            end_time = datetime.now()
            
            # Try to retrieve valid Turtle from raw output
            raw_output = response.content
            turtle_output = retrieve_parsable_turtle(raw_output)
            
            # Save parsed output if it includes valid Turtle
            if turtle_output is not None:
                try:
                    with open(parsed_output_path, "w", encoding="utf-8") as turtle_file:
                        turtle_file.write(turtle_output)
                    logger.info(f"Saved parsed output to {parsed_output_path}")
                except Exception as e:
                    logger.error(f"Error saving parsed output: {e}")
                
            # Fetch metadata, rendered prompt, and raw response
            metadata = {
                "mode": mode,
                "model": model.model_name,
                "valid_turtle": False if turtle_output is None else True,
                "test_file": test_file,
                "timestamp": start_time.isoformat(),
                "runtime": (end_time - start_time).total_seconds(),
                "parsed_output_path": None if turtle_output is None else parsed_output_path,
                "token_usage": response.response_metadata["token_usage"],
                "finish_reason": response.response_metadata["finish_reason"]
            }
            
            results[run_key] = {
                "metadata": metadata,
                "rendered_prompt": prompt_handler.rendered_prompt,
                "raw_response": response.content,
            }
        
        # Save raw outputs
        raw_output_path = os.path.join(experiment_dir, model.model_name, "output", f"{mode}_{model.model_name}_raw_output.json")
        with open(raw_output_path, 'w', encoding='utf-8') as json_file:
            json.dump(results, json_file, ensure_ascii=False, indent=4)
        logger.info(f"Saved raw outputs to {raw_output_path}")
        
    logger.info(f"{mode.capitalize()} experiment completed!")
    
def main(test_dir: str, prompt_components_dir: str, results_dir: str, mode: str, api_key: str, base_url: str, train_dir: str = None, examples: int = None):
    """
    Checks if the mode is supported and, if so, runs thecorresponding experiment.

    :param test_dir: Directory containing test files.
    :param prompt_components_dir: Directory wiht components for constructing prompts.
    :param results_dir: Directory to save the experiment results.
    :param mode: Experiment mode (e.g., "baseline", "fewshot").
    :param api_key: API key for authenticating requests to Chat-AI API.
    :param base_url: Base URL for the Chat-AI API endpoint.
    :param train_dir: (Optional) Directory containing in-context examples.
    :param examples: (Optional) Number of examples for few-shot experiments.
    """
    # Check if mode is supported
    try:
        # Normalize mode name
        mode = next(key for key, mode_data in supported_modes.items() if mode.lower() == key or mode.lower() in mode_data["synonyms"])
    except StopIteration:
        logger.error(f"Unsupported mode: {mode}. Supported modes: {supported_modes.keys()}")
        return

    model_handler = ModelHandler(api_key=api_key, base_url=base_url)
    
    if mode == "baseline":
        run_baseline_experiment(test_dir, prompt_components_dir, model_handler, results_dir)
    elif mode == "fewshot":
        run_fewshot_experiment(test_dir, prompt_components_dir, model_handler, results_dir, train_dir, examples)
    else:
        return
    
    
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate SHACL shapes from benefit descriptions using the specified prompting method.")
    parser.add_argument("test_dir", type=str, help="Directory with benefits used for inference.")
    parser.add_argument("prompt_resources_dir", type=str, help="Directory with ontology and instruction files.")
    parser.add_argument("results_dir", type=str, help="Directory to save results from all experiments.")
    parser.add_argument("mode", type=str, choices=["baseline", "fewshot"], help="Name of experiment.")
    parser.add_argument("api_key", type=str, help="API key for authenticating requests to Chat-AI API.")
    parser.add_argument("base_url", type=str, help="Base URL for the Chat-AI API endpoint.")
    parser.add_argument("--train_dir", type=str, default=None, help="Directory containing in-context examples.")
    parser.add_argument("--examples", type=int, default=None, help="Number of examples for few-shot experiments.")
    
    args = parser.parse_args()
    main(args)