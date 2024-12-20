""" 
prompt_template.py

Classes for loading individual prompt components and combining them
into a template.
"""

from preprocessing.dataset.groundtruth_templates import extract_benefit_information
from preprocessing.utils import read_file
from typing import List
import random
import os

class PromptComponents:
    """
    Loads components of a prompt and merges them into a prompt template.

    Attributes:
        ontology (str): Ontology that serves as context.
        instruction (str): Task description in natural language.
        input (str): Input string including name, idlbs and requirements text of a social benefit.
        template (str): String that combines individual prompt components.

    Methods:
        construct_template(mode: str) -> str:
            Constructs a template based on the specified prompting mode.
    """
    _ontology_cache = None

    def __init__(self, ontology_path: str, instruction_path: str, test_path: str, train_dir: str, mode: str = "baseline"):
        if PromptComponents._ontology_cache is None:
            PromptComponents._ontology_cache = read_file(ontology_path)
            
        self.ontology = PromptComponents._ontology_cache
        self.instruction = read_file(instruction_path)
        self.requirements = self._get_requirements(test_path)
        self.template = self._get_template(mode)
        self.input_variables = self._get_input_variables(mode)
        self.examples = self._get_random_examples(mode, train_dir)

    def _get_requirements(self, input_path: str) -> str:
        """Loads name, idlb, requirements text and, optionally, groundtruth SHACL shape for a benefit."""
        name, idlb, requirements = extract_benefit_information(input_path)
        return (f"Name: {name}\nIDLB: {idlb}\nRequirements text: {requirements}\nSHACL:\n")
    
    def _get_template(self, mode: str) -> str:
        """Returns a template depning on the prompting mode."""
        if mode not in {"baseline", "oneshot", "fewshot"}:
            raise ValueError("Invalid mode. Use 'baseline', 'oneshot', 'fewshot'.")
        
        # Base components included in each prompt
        components = [ "--- INSTRUCTION ---\n\n{instruction}\n\n",
                      "--- CONTEXT ---\n\n{ontology}\n\n",
                      "--- INPUT ---\n\n{input}\n\n"
                      ]
        
        # Additional components depending on prompting technique
        if mode in ["oneshot", "fewshot"]:
            components[-1:-1] = ["--- EXAMPLES ---\n\n{example}\n\n"]
        
        return "".join(components)

    def _get_input_variables(self, mode: str) -> List[str]:
        """Returns a list of input variables based on the prompting mode."""
        if mode == "baseline":
            return ["instruction", "ontology", "input"]
        elif mode in ["oneshot", "fewshot"]:
            return ["instruction", "ontology", "examples", "input"]
        else:
            raise ValueError("Invalid mode. Use 'baseline' or 'fewshot'.")
        # TODO: Extend for more modes
    
    def _get_random_examples(self, mode: str, train_dir: str) -> str:
        """Retrieve in-context examples based on the specified mode."""
        num_examples = {"baseline": 0, "oneshot": 1, "fewshot": 2}.get(mode, 0)
        return ExampleRetriever(train_dir, num_examples)
   
class ExampleRetriever():
    """Returns an in-context example."""
    def __init__(self, train_dir, num_examples=0):
        self.train_dir = train_dir
        self.examples_list = []
        self.examples_string = ""
        
        if num_examples > 0:
            self._select_random_examples(num_examples)

    def _select_random_examples(self, num_examples):
        # Gather all training files ending with '_text.json'
        train_files = [os.path.join(self.train_dir, file) for file in os.listdir(self.train_dir) if file.endswith("_text.json")]

        # Select the requested number of random files
        selected_files = random.sample(train_files, min(num_examples, len(train_files)))

        # Process each selected file
        examples = []
        for train_file in selected_files:
            name, idlb, requirements = extract_benefit_information(train_file)
            groundtruth_path = train_file.replace("data/input/train/", "data/groundtruth/shacl_gold/").replace("_text.json", "_gold.ttl")
            
            with open(groundtruth_path, "r", encoding="utf-8") as f:
                groundtruth = f.read()

            examples.append(f"Name: {name}\nIDLB: {idlb}\nRequirements text: {requirements}\nSHACL:\n{groundtruth}")
            self.examples_list.append(name)

        self.examples_string = "\n---\n".join(examples)

# EXAMPLE USAGE
if __name__ == "__main__":
    
    # Example retriever
    train_dir = "path/to/train"
    num_examples = 2
    retriever = ExampleRetriever(train_dir, num_examples)
    print(retriever.examples_string)
    print(retriever.examples_list)
    
    # Prompt template with examples
    ontology_path = "path/to/ontology.ttl"
    instruction_path = "path/to/instructions.txt"
    test_path = "path/to/test.json"
    
    prompt = PromptComponents(ontology_path, instruction_path, test_path, train_dir, mode="fewshot")
    
    print(prompt.ontology)
    print(prompt.instruction)
    print(prompt.requirements)
    print(prompt.template)
    print(prompt.input_variables)
    print(prompt.examples)