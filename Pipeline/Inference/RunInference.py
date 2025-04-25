""" 
RunInference.py

- Run experiments to generate SHACL shapes graphs from requirements texts 
    using various prompting strategies.
- Supported prompting strategies: baseline, few-shot, and chain-of-thought 
    with vairable number of examples and k-fold cross-validation.
- Save the generated SHACL graphs in Turtle format and metadata and raw
    output in JSON format.
"""

import os
import json
import time
import logging
import argparse
from typing import List, Tuple
from sklearn.model_selection import KFold
from openai import RateLimitError
from langchain_openai.chat_models.base import ChatOpenAI
from .Model import ModelHandler
from .Prompt import PromptHandler
from Utils.Logger import setup_logger
from Utils.FileHandling import setup_experiment_directory
from Utils.Parsing import retrieve_parsable_turtle, get_idlb_from_label, normalize_mode, generate_parsed_output_path
from resources.schemata.method_schema import supported_modes

# Constants
MAX_RETRIES = 3
INITIAL_DELAY = 60


def validate_mode_params(mode: str, num_examples: int, k: int) -> Tuple[int, int]:
    """Checks if the requested mode and parameters valid.
    
    :param mode: Requested prompting strategy.
    :param num_examples: Requested number of examples.
    :param k: Requested number of folds for k-fold cross validation.
    
    :return: Tuple of validated num_examples and k.
    """
    # Lowercase and replace synonyms with the canonical name
    mode = normalize_mode(mode)
    # Feshot and cot require at least 1 example and 2 folds
    if mode in ["fewshot", "cot"]:
        if num_examples <= 0:
            raise ValueError("Number of examples must be greater than 0 for fewshot or cot mode.")
        if k < 2:
            raise ValueError("Number of folds must be at least 2 for k-fold cross-validation.")
    # Baseline only runs with 0 examples and 0 folds
    elif mode == "baseline":
        if num_examples > 0 or k > 0:
            print("Number of examples and folds will be ignored in baseline mode.")
        num_examples, k = 0, 0
    else:
        raise ValueError(f"Unsupported mode: {mode}. "
                         f"Supported modes are: {supported_modes.keys()}")

    return mode, num_examples, k


def invoke_model_with_retry(prompt_handler: PromptHandler, model: ChatOpenAI, logger: logging.Logger) -> Tuple[str, str, float, dict]:
    """Invokes an LLM with retry logic on rate limit errors.
    
    :param prompt_handler: Instance for generating prompts.
    :param model: Instance of ChatOpenAI for generating LLM output.
    :param logger: Logger instance.
    
    :return: Model response, start time, and elapsed time.
    """
    retries = 0
    delay = INITIAL_DELAY
    response = None
    start_time = time.time()
    
    while retries <= MAX_RETRIES:
        try:
            chain = prompt_handler.prompt_template | model
            response = chain.invoke(prompt_handler.prompt_components)
            finish_reason = response.response_metadata["finish_reason"]
        # Retry with exponential backoff on rate limit error
        except RateLimitError as e:
            retries += 1
            if retries > MAX_RETRIES:
                logger.error(f"Rate limit exceeded after {MAX_RETRIES} retries: {e}")
                finish_reason = (f"Rate limit exceeded after max retries hit: {str(e)}")
                break
            logger.warning(f"Rate limit hit. Retrying in {delay}s...")
            time.sleep(delay)
            delay *= 2
        except Exception as e:
            logger.error(f"Error invoking {model.model_name}: {e}")
            finish_reason = (str(e))
            break
    elapsed_time = time.time() - start_time
    
    return response, finish_reason, start_time, elapsed_time


def process_file(filepath: str, 
                 mode:str, 
                 model: ChatOpenAI, 
                 prompt_components_dir: str,
                 parsed_output_dir: str, 
                 logger: logging.Logger, 
                 groundtruth_dir: str = None, 
                 train_files: List[str] = [], 
                 num_examples: int = 0) -> List[dict]:
    """Generates SHACL graph from a natural language text.
    
    Prompts an LLM using the specified mode. If the model generates parsable
    Turtle content, it is saved to a file.
    
    :param filepath: Path to the input file.
    :param model: Instance of ChatOpenAI for generating LLM output.
    :param prompt_components_dir: Directory containing the prompt components.
    :param parsed_output_dir: Directory to save the parsed output.
    :param logger: Logger instance.
    :param groundtruth_dir: Directory with SHACL gold files for examples.
    :param train_files: List of files from which examples are sampled.
    :param num_examples: Number of examples for fewshot or cot modes.
    
    :return: Summary of results including metadata, rendered prompt and
        raw response.
    """
    prompt_handler = PromptHandler(
        mode=mode,
        input_path=filepath,
        prompt_components_dir=prompt_components_dir,
        groundtruth_dir=groundtruth_dir,
        train_files=train_files or [],
        num_examples=num_examples,
        logfile=logger.log_file
    )
    
    logger.info(f"Invoking {model.model_name}...")
    response, finish_reason, start_time, elapsed_time = invoke_model_with_retry(prompt_handler, model, logger)
    
    # Extract information identifying the run
    benefit_name = os.path.splitext(os.path.basename(filepath))[0]
    idlb = get_idlb_from_label(label_type="snake case", label_value=benefit_name, logfile=logger.log_file)
    run_key = f"{mode}_{model.model_name}_{benefit_name.replace('_', '-')}"
    
    # Summarize metadata
    metadata = {
        "mode": mode,
        "model": model.model_name,
        "test_benefit": benefit_name,
        "test_filepath": filepath,
        "test_idlb": idlb,
        "examples_idlb": prompt_handler.selected_examples_id, # empty list if no examples
        "timestamp": time.strftime("%D %H:%M:%S", time.gmtime(start_time)),
        "runtime (sec)": elapsed_time,
        "finish_reason": finish_reason
    }
    
    # If the run was successful, search for valid Turtle content in the raw output
    raw_response, token_usage = None, None
    if response:
        raw_response = response.content
        token_usage = response.response_metadata["token_usage"]
        turtle_output = retrieve_parsable_turtle(response.content, logifle=logger.log_file)
        parsed_output_path = generate_parsed_output_path(turtle_output, parsed_output_dir, run_key, logger.log_file)

        metadata.update({
            "valid_turtle": int(turtle_output is not None),
            "parsed_output_path": parsed_output_path,
            "token_usage": token_usage,
        })
 
    return {
        "run_key": run_key,
        "metadata": metadata,
        "rendered_prompt": prompt_handler.rendered_prompt,
        "raw_response": raw_response,
    }


def run_experiment(test_dir: str, 
                   prompt_components_dir: str, 
                   results_dir: str,
                   mode: str, 
                   api_key: str, 
                   base_url: str, 
                   custom_models: List[str] = None,
                   groundtruth_dir: str = None, 
                   num_examples: int = 0, 
                   k: int = 0) -> str:
    """Runs a prompting experiment with the specified mode and parameters.
    
    :param test_dir: Directory containing the test files.
    :param prompt_components_dir: Directory containing the prompt components.
    :param results_dir: Directory to save the results.
    :param mode: Prompting strategy to use.
    :param api_key: API key for Chat-AI API.
    :param base_url: Base URL for the Chat-AI API endpoint.
    :param num_examples: Number of examples for fewshot or cot modes.
    :param k: Number of folds for k-fold cross-validation (only for fewshot or cot).
    :param groundtruth_dir: Directory containing SHACL gold files for examples.
    :param custom_models: Optional list of custom model names to use.
    
    :return: Name of the experiment.
    """
    start_time_total = time.time()
    
    # Ensure valid parameters are provided for the selected mode
    mode, num_examples, k = validate_mode_params(mode, num_examples, k)
    experiment_name = f"{mode}_{num_examples}ex{k}fcv_{int(start_time_total)}"
    
    logger = setup_logger(__name__, f"logs/{experiment_name}.log")
    logger.info(f"Running {mode} experiment with {num_examples} examples and {k} folds...")
    
    model_handler = ModelHandler(api_key=api_key, base_url=base_url, logfile=logger.log_file)
    
    # Use custom models if provided, else default models depending on the mode
    model_keys = (
        custom_models if custom_models
        else model_handler.base_models if mode == "baseline"
        else model_handler.main_model
    )
    models = [model_handler.initialize_model(key) for key in model_keys]
    
    experiment_dir = os.path.join(results_dir, experiment_name)
    os.makedirs(experiment_dir, exist_ok=True)
    
    for i, model in enumerate(models):        
        parsed_output_dir = os.path.join(experiment_dir, model.model_name, "output", "parsed_output")
        os.makedirs(parsed_output_dir, exist_ok=True)
        
        results = []
                
        # Process each file sequentially for baseline mode
        if mode == "baseline":
            test_files = [os.path.join(test_dir,filename) for filename in os.listdir(test_dir)]
            for file_index, filepath in enumerate(test_files):
                logger.info(f"Processing file {filepath} ({file_index+1}/{len(test_files)}) with model {model.model_name} ({i+1}/{len(models)})")
                result = process_file(filepath, mode, model, prompt_components_dir, parsed_output_dir, logger)
                results.append(result)
        # Run with k-fold cross-validation for fewshot and cot modes
        elif mode in ["fewshot", "cot"]:
            kf = KFold(n_splits=k, shuffle=True, random_state=42)
            all_files = os.listdir(test_dir)

            file_count = 0
            for fold_index, (train_indices, test_indices) in enumerate(kf.split(all_files)):
                train_files = [os.path.join(test_dir, all_files[i]) for i in train_indices]
                test_files = [os.path.join(test_dir, all_files[i]) for i in test_indices]
                logger.info(
                    f"Fold {fold_index + 1}/{k} | "
                    f"Train files: {[all_files[i] for i in train_indices]} | " 
                    f"Test files: {[all_files[i] for i in test_indices]}"
                )

                for file_index, filepath in enumerate(test_files):
                    logger.info(f"Processing file {os.path.basename(filepath)} ({file_count+1}/{len(all_files)}) with model {model.model_name} ({i+1}/{len(models)})")
                    result = process_file(filepath, mode, model, prompt_components_dir, parsed_output_dir, logger,
                                          groundtruth_dir, train_files, num_examples)
                    result["metadata"]["fold"] = fold_index + 1
                    results.append(result)
                    file_count += 1
        
        # Save raw output and metadata for the entire run to JSON file                   
        raw_output_path = os.path.join(experiment_dir, model.model_name, "output", f"raw_output.json")
        with open(raw_output_path, 'w', encoding='utf-8') as json_file:
            json.dump(results, json_file, ensure_ascii=False, indent=4)
        logger.info(f"Saved raw outputs to {os.path.abspath(raw_output_path)}")
    
    elapsed_time_total = (time.time() - start_time_total) / 60
    logger.info(f"{mode.capitalize()} experiment completed! Total runtime: {elapsed_time_total:.2f} minutes.")
    
    return experiment_name
    

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Run LLM prompting experiment for SHACL generation from text.")
    parser.add_argument("--test_dir", required=True, help="Directory containing the test files.")
    parser.add_argument("--prompt_components_dir", required=True, help="Directory containing the prompt components")
    parser.add_argument("--results_dir", required=True, help="Directory to save the results.")
    parser.add_argument("--mode", required=True, choices=["baseline", "fewshot", "cot"], help="Prompting strategy to use.")
    parser.add_argument("--api_key", required=True, help="API key for Chat-AI API.")
    parser.add_argument("--base_url", required=True, help="Base URL for the Chat-AI API endpoint.")
    parser.add_argument("--num_examples", type=int, default=0, help="Number of examples for fewshot or cot modes.")
    parser.add_argument("--k", type=int, default=0, help="Number of folds for k-fold cross-validation.")
    parser.add_argument("--groundtruth_dir", help="Directory containing SHACL gold files for examples")
    parser.add_argument("--custom_models", nargs="+", help="Optional list of custom model names to use.")

    args = parser.parse_args()

    run_experiment(
        test_dir=args.test_dir,
        prompt_components_dir=args.prompt_components_dir,
        results_dir=args.results_dir,
        mode=args.mode,
        api_key=args.api_key,
        base_url=args.base_url,
        custom_models=args.custom_models,
        groundtruth_dir=args.groundtruth_dir,
        num_examples=args.num_examples,
        k=args.k
    )