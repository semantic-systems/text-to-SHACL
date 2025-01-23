""" 
Prompt.py

Class to dynamically construct and render prompts based on a specified mode. 
"""

import os
import json
import random
from typing import Any, Dict, Optional
from langchain_core.prompts import PromptTemplate
from resources.schemata.modes_schema import supported_modes
from Utils.Logger import setup_logger

logger = setup_logger(__name__, "logs/Prompt.log")

class PromptHandler:
    """
    Constructs and renders prompts based on the specified mode. Renders the
    prompt and prompt template as an instance of LangChain's PromptTemplate
    class.

    :attr mode: Name of the prompt experiment, e.g., "baseline"
    :attr prompt_components_dir: Directory containing resource files for prompt components.
    :attr prompt_variables: List of variable names required for the prompt in the specified mode.
    :attr prompt_template: Prompt with placeholders for variables.
    :attr prompt_components: Loaded components mapped to their variable names.
    :attr rendered_prompt (str): The fully rendered prompt with all variables replaced.
    """
    def __init__(self, mode: str, input_path: str, prompt_components_dir: str, num_examples: Optional[int] = None, train_dir: Optional[str] = None):
        self.mode = mode
        self.train_dir = train_dir
        self.num_examples = num_examples
        self.examples = []
        self.prompt_components_dir = prompt_components_dir
        self.prompt_variables = supported_modes[mode]["prompt_variables"]
        self.prompt_template = PromptTemplate(template=self._load_prompt_template()) # e.g. "Tell me a fun fact about {animal}."
        
        # Load variable prompt components and fixed input component
        self.prompt_components = {} # e.g. {"animal": "wombats"}
        for variable in self.prompt_variables:
            load_method = getattr(self, f"_load_{variable}", None)
            if callable(load_method):
                self.prompt_components[variable] = load_method()
            else:
                logger.error(f"No loader method defined for prompt variable: {variable}")
                raise
        self.prompt_components["input"] = self.load_input(input_path)
        
        self.rendered_prompt = self.prompt_template.format(**self.prompt_components) # e.g. "Tell me a fun fact about wombats."
        
    def _load_file(self, file_path: str, as_json: bool = False) -> Any:
        """Utility function to load file content as text or JSON."""
        try:
            with open(file_path, 'r', encoding = "utf-8") as file:
                return json.load(file) if as_json else file.read()
        except FileNotFoundError as e:
            logger.error(f"Failed to load prompt component. File not found: {file_path}")
            raise
        
    def _load_shacl_gold_from_idlb(self, idlb: str) -> str:
        """Returns the SHACL groundtruth for the benefit with the specified IDLB."""
        groundtruth_base_dir = os.path.abspath(os.path.join(self.train_dir, os.pardir, os.pardir, "shacl_gold"))
        groundtruth_path = os.path.join(groundtruth_base_dir, f"{idlb}_gold.ttl")
        shacl_gold_string = self._load_file(groundtruth_path)
        return shacl_gold_string

    def _load_prompt_template(self) -> str:
        """Returns the prompt template for the specified mode."""
        template_path = os.path.join(self.prompt_components_dir, self.mode, f"prompt_template.txt")
        return self._load_file(template_path)
    
    def _load_instruction(self) -> str:
        """Returns the instruction for the specified mode."""
        instruction_path = os.path.join(self.prompt_components_dir, self.mode, f"instruction.txt")
        return self._load_file(instruction_path)
    
    def _load_ontology(self) -> str:
        """Returns the ontology for the specified mode."""
        ontology_path = os.path.join(self.prompt_components_dir, f"ontology/ontology.ttl")
        return self._load_file(ontology_path)
    
    def load_input(self, file_path: str) -> str:
        """Returns the model input for a given test or train file."""
        # Extract the benefit name, IDLB, and requirements text
        with open(file_path, 'r', encoding='utf-8') as json_file:
            description = json.load(json_file)
        name, idlb,requirements_text = description["name"], description["idlb"], description["requirements"]
        
        # Construct the input text
        intro = "Es folgen die Bedingungen für die Sozialleistung '{name}' mit der IDLB {idlb}.\n"
        input = intro.replace("{name}", name).replace("{idlb}", idlb) + requirements_text
        
        return input
    
    def _load_fewshot_examples(self) -> str:
        """Returns string of randomly selected examples from the train split."""        
        if not self.train_dir:
            logger.error("Train directory not provided.")
            raise ValueError("Train directory not provided.")
        if self.num_examples > len(os.listdir(self.train_dir)):
            logger.error(f"Number of examples requested exceeds the number of files in the train directory: {self.train_dir}")
            raise ValueError("Number of examples requested exceeds the number of files in the train directory.")
        
        # Get all example files in the train directory
        train_files = [
            benefit for benefit in os.listdir(self.train_dir) 
            if os.path.isfile(os.path.join(self.train_dir, benefit)) and benefit.endswith(".json")
        ]
        
        # Randomly select the specified number of example files
        selected_examples = random.sample(train_files, self.num_examples)
        logger.info(f"Selected examples: {selected_examples}")
        
        examples = [] 
        for example in selected_examples:
            idlb = os.path.splitext(example)[0]
            self.examples.append(idlb)
            
            # Load input from the train file
            input_path = os.path.join(self.train_dir, example)
            example_input = self.load_input(input_path)
            
            # Load corresponding SHACL groundtruth
            shacl_gold = self._load_shacl_gold_from_idlb(idlb)
            
            # Load example template and replace placeholders
            example_template_path = os.path.join(self.prompt_components_dir, self.mode, "example_template.txt")
            example_template = self._load_file(example_template_path)
            example_string = example_template.replace("{train_input}", example_input).replace("{shacl_gold}", shacl_gold)
            examples.append(example_string)
        
        # Concatenate all example strings
        examples_string = "\n\n".join(examples)
        
        return examples_string