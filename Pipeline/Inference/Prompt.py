""" 
Prompt.py

Class to construct and render prompts based on a specified mode.
Supported modes include baseline (no examples), fewshot (variable
number of examples), and chain-of-thought (CoT) prompting.
Where applicable, examples are retrieved based on the similarity
of input embeddings.
"""

import os
import json
from typing import List
from langchain_core.prompts import PromptTemplate
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_core.example_selectors import SemanticSimilarityExampleSelector
from langchain_chroma import Chroma
from Utils.FileHandling import load_file
from Utils.Parsing import get_idlb_from_intro, get_decomposition_section
from Utils.Logger import setup_logger
from resources.schemata.ids_schema import idlb_to_labels


API_KEY = os.getenv("GWDG_API_KEY") # API key for the GWDG service
BASE_URL = os.getenv("GWDG_BASE_URL") # Base URL for the GWDG service

class PromptHandler:
    """
    Constructs and renders prompts based on the specified mode. Renders the
    prompt and prompt template as an instance of LangChain's PromptTemplate
    class.

    :attr mode: Name of the prompting strategy.
    :attr input_path: Path to the input file for the test set.
    :attr prompt_components_dir: Directory containing the content for prompt components.
    :attr groundtruth_dir: Directory containing the SHACL gold files.
    :attr logger: Logger instance. Defaults to a file-speicific logger.
    :attr train_files: List of training file paths.
    :attr num_examples: Number of fewshot examples to include in the prompt.
    :attr prompt_template: Lang chain object including input variables and prompt layout.
    :attr prompt_components: Mapping of variables to loaded content.
    :attr rendered_prompt: The filled-in prompt template.
    """
    def __init__(self, 
                 mode: str, 
                 input_path: str, 
                 prompt_components_dir: str,
                 groundtruth_dir: str,
                 logfile: str = "logs/PromptHandler.log", 
                 train_files: List[str] = [],
                 num_examples: int = 0):
        self.mode = mode
        self.prompt_components_dir = prompt_components_dir
        self.groundtruth_dir = groundtruth_dir
        self.logger = setup_logger(__name__, logfile)
        self.test_file = input_path
        self.train_files = train_files
        self.num_examples = num_examples
        self.selected_examples_id = []
        
        tmpl_path = os.path.join(self.prompt_components_dir, self.mode, f"prompt_template.txt")
        self.prompt_template = PromptTemplate(template=load_file(file_path=tmpl_path, logger=self.logger)) # e.g. PromptTemplate(input_variables=["animal"], template="Tell me a fun fact about {animal}.)"
        
        # Load the content of the individual prompt components
        self.prompt_components = {} # e.g. {"animal": "wombat"} 
        # Prioritize loading of "input" before any other variables
        sorted_variables = sorted(
            self.prompt_template.input_variables,
            key=lambda v: (v != "input")
        )
        sorted_variables
        for variable in sorted_variables:
            load_method = getattr(self, f"_load_{variable}", None)
            if callable(load_method):
                self.prompt_components[variable] = load_method()
            else:
                raise ValueError(f"No loader method defined for prompt variable: {variable}")
        
        self.rendered_prompt = self.prompt_template.format(**self.prompt_components) # e.g. "Tell me a fun fact about wombats."
        
    def _load_shacl_gold(self, input_filename: str) -> str:
        """Returns the SHACL groundtruth for input file."""
        shacl_filename = os.path.splitext(input_filename)[0] + ".ttl"
        shacl_gold_path = os.path.join(self.groundtruth_dir, shacl_filename)
        return load_file(file_path=shacl_gold_path, logger=self.logger)

    def _load_prompt_template(self, template_path: str) -> str:
        """Returns the prompt template for the specified mode."""
        template_path = os.path.join(self.prompt_components_dir, self.mode, f"prompt_template.txt")
        return load_file(file_path=template_path, logger=self.logger)
    
    def _load_instruction(self) -> str:
        """Returns the instruction for the specified mode."""
        instruction_path = os.path.join(self.prompt_components_dir, self.mode, f"instruction.txt")
        return load_file(file_path=instruction_path, logger=self.logger)
    
    def _load_ontology(self) -> str:
        """Returns the ontology."""
        ontology_path = os.path.join(self.prompt_components_dir, f"ontology/ontology.omn")
        return load_file(file_path=ontology_path, logger=self.logger)
    
    def _load_input(self, filepath: str = None) -> str:
        """Returns the model input for a given test or train file."""
        if filepath is None:
            filepath = self.test_file
        
        # Extract the benefit name, IDLB, and requirements text
        with open(filepath, 'r', encoding='utf-8') as json_file:
            description = json.load(json_file)
        name, idlb,requirements_text = description["name"], description["idlb"], description["requirements"]
        
        # Add an introductory sentence
        intro = "Es folgen die Bedingungen für die Sozialleistung '{name}' mit der IDLB {idlb}.\n"
        input = intro.replace("{name}", name).replace("{idlb}", idlb) + requirements_text
        
        return input
    
    def _select_semantic_similarity_examples(self) -> List:
        # Generate list of correct input-output pairs
        examples = []
        for train_file in self.train_files:
            text = self._load_input(train_file)
            shacl = self._load_shacl_gold(os.path.basename(train_file))
            examples.append({"text": text, "shacl": shacl})
        
        # Prepare embedding model
        model_name = "sentence-transformers/all-mpnet-base-v2"
        model_kwargs = {'device': 'cuda'}
        encode_kwargs = {'normalize_embeddings': False}
        embeddings = HuggingFaceEmbeddings(
            model_name=model_name,
            model_kwargs=model_kwargs,
            encode_kwargs=encode_kwargs
        )

        # Select examples based on similarity of input embeddings
        example_selector = SemanticSimilarityExampleSelector.from_examples(
            examples,
            embeddings=embeddings,
            vectorstore_cls=Chroma,
            k=self.num_examples,
        )
        selected_examples = example_selector.select_examples({"input": self.prompt_components["input"]})

        return selected_examples
        
    def _load_fewshot_examples(self) -> str:
        """Returns fewshot examples from train set.
        
        Each example includes:
            - Input: Eligibility requirements for a social benefit.
            - Output: The corresponding ground truth SHACL graph.
        They are selected based on the similarity of input embeddings.
        """        
        selected_examples = self._select_semantic_similarity_examples()
        example_tmpl_path = os.path.join(self.prompt_components_dir, self.mode, f"example_template.txt")
        
        examples = []
        for example in selected_examples:
            text, shacl = example["text"], example["shacl"]
            
            # Populate the fewshot example template
            example_tmpl = load_file(file_path=example_tmpl_path, logger=self.logger)
            example_string = example_tmpl.replace("{text}", text).replace("{shacl}", shacl).rstrip()
            examples.append(example_string)
            
            # Store selected example
            _, idlb = get_idlb_from_intro(text)
            self.selected_examples_id.append(idlb)
       
        return "\n\n\n".join(examples)
    
    def _load_cot_examples(self) -> str:
        """Returns chain-of-thought examples from train set.
        
        Each example includes:
            - Input: Eligibility requirements for a social benefit.
            - Output: A step-by-step solution including the corresponding 
                ground truth SHACL graph at the end.
        They are selected based on the similarity of input embeddings.
        """
        selected_examples = self._select_semantic_similarity_examples()
        example_tmpl_path = os.path.join(self.prompt_components_dir, self.mode, f"example_template.txt")
        requirements_en_dir = os.path.join(self.prompt_components_dir, self.mode, "requirements_text_en")
        decomposition_dir = os.path.join(os.path.dirname(self.prompt_components_dir), "requirements_decomposition")
        
        examples = []
        for example in selected_examples:
            text, shacl = example["text"], example["shacl"]
            
            # Load example output for step 1 (translate and structure the input)
            benefit_de, idlb = get_idlb_from_intro(text)
            benefit_en = idlb_to_labels[idlb]["english label"]
            benefit_snake = idlb_to_labels[idlb]["snake case"]
            requirements_en = load_file(file_path=os.path.join(requirements_en_dir, f"{benefit_snake}.txt"), logger=self.logger)   
            structured_text = (
                f"Benefit (DE / EN): {benefit_de} (DE) / {benefit_en} (EN)\n"
                f"IDLB: {idlb}\n"
                f"Requirements text (EN): {requirements_en}"
            )
            
            # Load example output for step 2 (extract individual requirements)
            decomposition = get_decomposition_section(os.path.join(decomposition_dir, f"{benefit_snake}.md"), self.logger)   
            
            # Populate the chain of thought example template
            example_tmpl = load_file(file_path=example_tmpl_path, logger=self.logger)
            example_string = example_tmpl.replace("{text}", text).replace("{structured_text}", structured_text).replace("{decomposition}", decomposition).replace("{shacl}", shacl).rstrip()
            examples.append(example_string)
            
            self.selected_examples_id.append(idlb)
       
        return "\n\n\n".join(examples)