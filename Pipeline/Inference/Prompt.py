""" 
Prompt.py

Class to dynamically construct and render prompts based on a specified mode. 
"""

import os
import json
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
        self.prompt_components_dir = prompt_components_dir
        self.prompt_variables = supported_modes[mode]["prompt_variables"]
        self.prompt_template = PromptTemplate(
            input_variables=self.prompt_variables, template=self._load_prompt_template()
            ) # e.g. "Tell me a fun fact about {animal}."
        
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

    def _load_prompt_template(self) -> str:
        """Loads the prompt template for the specified mode."""
        template_path = os.path.join(self.prompt_components_dir, self.mode, f"prompt_template.txt")
        return self._load_file(template_path)
    
    def _load_instruction(self) -> str:
        """Loads the instruction for the specified mode."""
        instruction_path = os.path.join(self.prompt_components_dir, self.mode, f"instruction.txt")
        return self._load_file(instruction_path)
    
    def _load_ontology(self) -> str:
        """Loads the ontology for the specified mode."""
        ontology_path = os.path.join(self.prompt_components_dir, f"ontology/ontology.ttl")
        return self._load_file(ontology_path)
    
    def load_input(self, file_path: str) -> str:
        """Loads the model input for a given test or train file."""
        # Extract the benefit name, IDLB, and requirements text
        with open(file_path, 'r', encoding='utf-8') as json_file:
            description = json.load(json_file)
        name, idlb,requirements_text = description["name"], description["idlb"], description["requirements"]
        
        # Construct the input text
        intro = "The following requirements must be met to be eligible for the benefit '{name}' with the IDLB {idlb}.\n"
        input = intro.replace("{name}", name).replace("{idlb}", idlb) + requirements_text
        
        return input
    
    def _load_examples(self) -> Dict[str, Any]:
        """Loads the examples for the specified mode."""
        pass