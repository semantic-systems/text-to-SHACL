""" 
api_access.py

Master's Thesis
Seike Appold

Defines a class for interacting with the GWDG ChatAI API 
(https://docs.hpc.gwdg.de/services/chat-ai/).
"""

import os
import requests
from typing import List, Optional, Dict, Any
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from langchain_core.prompts import ChatPromptTemplate

# Load API configurations
load_dotenv()

class ChatAIHandler:
    """
    Handles interactions with the GWDG ChatAI API, including retrieving available models 
    and initializing model instances with customizable configurations.

    Attributes:
        api_key (str): API key for authentication.
        base_url (str): Base URL for the API.
        available_models (List[str]): Cached list of available models.
        default_configs (Dict[str, Any]): Default model initialization parameters.

    Methods:
        get_available_models() -> List[str]:
            Retrieves a list of available models from the API.
            
        initialize_model(custom_configs: Optional[Dict[str, Any]] = None) -> ChatOpenAI:
            Initializes a model with the specified configurations.
    """
    # Cache list of available models
    _model_cache = None

    def __init__(self):
        self.api_key = os.getenv('GWDG_API_KEY')
        if not self.api_key:
            raise ValueError("GWDG_API_KEY environment variable is not set.")

        self.base_url = os.getenv('GWDG_BASE_URL')
        if not self.api_key:
            raise ValueError("GWDG_BASE_URL environment variable is not set.")

        # Use the cached models if available, otherwise fetch them
        if ChatAIHandler._model_cache is None:
            ChatAIHandler._model_cache = self.get_available_models()
        self.available_models = ChatAIHandler._model_cache

        self.default_configs = {
            "model_key": "meta-llama-3.1-8b-instruct",
            "temperature": 0,
            "top_p": None,
            "max_tokens": None,
            "logprobs": False,
            "timeout": None,
            "max_retries": 2
        }

    def get_available_models(self) -> List[str]:
        """Lists keys of all models available via the GWDG ChatAI API."""
        url = self.base_url + "/models"
        headers = {
            "Authorization": f"Bearer {self.api_key}"
        }

        response = requests.get(url, headers=headers)

        if response.status_code == 200:
            models = response.json()
            self.available_models = [model_key["id"] for model_key in models["data"]]
            return self.available_models
        else:
            response.raise_for_status()

    def initialize_model(self, custom_configs: Optional[Dict[str, Any]] = None) -> ChatOpenAI:
        """Initializes an instance of an OpenAI model with the specified parameters."""
        # Apply custom configurations if provided
        if not custom_configs:
            configs = self.default_configs
        else:
            # Check if config keys are valid
            if not set(custom_configs.keys()).issubset(self.default_configs.keys()):
                raise ValueError(f"Valid config keys: {[key for key in self.default_configs.keys()]}")
            # Merge default and custom configurations
            configs = {**self.default_configs, **custom_configs}

        # Check if specified model is available via the GWDG API
        if configs["model_key"] not in self.available_models:
            raise ValueError(f"Model {configs["model_key"]} is not available. \n"
                             f"Please choose from the following models: {self.available_models}")

        # Initialize an OpenAI model instance
        return ChatOpenAI(api_key=self.api_key,
                          base_url=self.base_url,
                          model_name=configs["model_key"],
                          temperature=configs["temperature"],
                          top_p=configs["top_p"],
                          max_tokens=configs["max_tokens"],
                          logprobs=configs["logprobs"],
                          timeout=configs["timeout"],
                          max_retries=configs["max_retries"])

# EXAMPLE USAGE
if __name__ == "__main__":
    handler = ChatAIHandler()
    
    # Retrieve available models
    print(handler.available_models)
    
    # Customize model configurations
    custom_configs = {
        "temperature": 1,
    }
    
    # Initialize a model instance
    model = handler.initialize_model(custom_configs)
    
    # Test the model with an example prompt
    prompt = ChatPromptTemplate.from_messages([
            ("system",
             "You are a computer scientist with a passion for semantic web technologies. "
             "Answer the following question. "),
            ("user", "{question}")
        ])
    chain = prompt | model
    question = "What is your favorite SHACL shape?"
    answer = chain.invoke(question)
    print(answer.content)