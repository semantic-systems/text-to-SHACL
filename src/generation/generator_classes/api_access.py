""" 
api_access.py

Class for interacting with the GWDG ChatAI API 
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
        self.base_url = os.getenv('GWDG_BASE_URL')
        if not self.api_key:
            raise ValueError("Environment variables 'GWDG_API_KEY' and 'GWDG_BASE_URL' must be set.")

        # Fetch available models if cache is empty
        if ChatAIHandler._model_cache is None:
            ChatAIHandler._model_cache = self.get_available_models()
        self.available_models = ChatAIHandler._model_cache
        
        # TODO: Update depending on results
        self.main_model = ["llama-3.1-nemotron-70b-instruct"]
        self.base_models = ["meta-llama-3.1-8b-instruct", "llama-3.1-nemotron-70b-instruct"]
        
        self.default_configs = {
            "temperature": 0,
            "top_p": None,
            "max_tokens": None,
            "logprobs": False,
            "timeout": 120,
            "max_retries": 2
        }

    def get_available_models(self) -> List[str]:
        """Retrieve list of available models from the API."""
        url = self.base_url + "/models"
        headers = {"Authorization": f"Bearer {self.api_key}"}
        response = requests.get(url, headers=headers)
        
        if response.status_code != 200:
            response.raise_for_status()
        models = response.json()
        return [model_key["id"] for model_key in models["data"]]
    
    def initialize_model(self, model_key: str="meta-llama-3.1-8b-instruct", custom_configs: Optional[Dict[str, Any]]=None) -> ChatOpenAI:
        """Initializes an instance of an OpenAI model with the specified parameters."""      
        if model_key not in self.available_models:
            raise ValueError(f"Invalid model key. Available models: {self.available_models}")

        configs = {**self.default_configs, **(custom_configs or {})}
        return ChatOpenAI(
            api_key=self.api_key,
            base_url=self.base_url,
            model_name=model_key,
            **configs,
        )

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
    model = handler.initialize_model(custom_configs=custom_configs)
  
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