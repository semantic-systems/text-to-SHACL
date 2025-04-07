"""  
Model.py

- Class for handling model interaction via Gesellschaft für wissenschaftliche
Datenverarbeitung Göttingen (GWDG) ChatAI API 
- Chat AI documentation: https://docs.hpc.gwdg.de/services/chat-ai/
"""
import requests
from typing import List, Optional, Dict, Any
from langchain_openai import ChatOpenAI
from Utils.Logger import setup_logger

logger = setup_logger(__name__, "logs/ModelHandler.log")

class ModelHandler:
    """ 
    Handles interactions with the GWDG ChatAI API, including retrieval of 
    available models and initialization of model instances with customizable
    configurations.

    :attr api_key: API key for authenticating requests to the model API.
    :attr base_url: Base URL for the model API endpoint.
    :attr available_models: List of models available through the API.
    :attr main_model: Main model selected for superior baseline performance.
    :attr base_models: A list of baseline models to be compared in the zeroshot setting.
    :attr default_configs: Default configuration parameters for model initialization.
    :attr _model_keys_cache: Stores the list of available model keys across class instances.
    """
    
    _model_keys_cache = None
    
    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url

        # Fetch available model keys if cache is empty
        if ModelHandler._model_keys_cache is None:
            logger.info("Fetching available model keys for the first time.")
            ModelHandler._model_keys_cache = self.get_available_model_keys(self.base_url, self.api_key)
        self.available_models = ModelHandler._model_keys_cache

        self.main_model = 'mistral-large-instruct' # TODO: Update depending on results
        self.base_models = ['meta-llama-3.1-8b-instruct', # meta
                            'qwq-32b', # alibaba cloud
                            'deepseek-r1-distill-llama-70b',
                            'llama-3.3-70b-instruct', # meta
                            'llama-3.1-sauerkrautlm-70b-instruct', # meta
                            'mistral-large-instruct', # mistral
                            'qwen2.5-72b-instruct', # alibaba cloud
                            ]
        self.default_configs = {
            # "temperature": 0.7, # Flattens/sharpens the probability distribution over tokens (high = more creative)
            # "top_p": 0.8, # Cumulative probability of tokens to sample from (high = more deterministic)
            # "max_tokens": None, # Max nof newly generated tokens
            # "logprobs": False, # Token level log probabilities
            "timeout": 90, # Seconds until API call times out
            "max_retries": 2 # Max nof retries after a failed API call
        }
        
    def get_available_model_keys(self, base_url: str, api_key: str) -> List[str]:
        """Returns a list of available model keys from the API."""
        url = base_url + "/models"
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            logger.error(f"Error fetching available model keys: {response.status_code}")
            response.raise_for_status()
        models = response.json()
        
        return [model_key["id"] for model_key in models["data"]]
    
    def initialize_model(self, model_key: str, custom_configs: Optional[Dict[str, Any]]=None) -> ChatOpenAI:
        """Returns an instance of an OpenAI model with customized configs, if any."""      
        logger.info(f"Initializing model with key: {model_key}")
        
        if model_key not in self.available_models:
            logger.error(f"Invalid model key. Available models: {self.available_models}")
            raise ValueError(f"Invalid model key: {model_key}")
        
        configs = {**self.default_configs, **(custom_configs or {})}
        
        try:
            model_instance = ChatOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                model_name=model_key,
                **configs,
            )
            logger.info(f"Model {model_key} initialized successfully.")
            return model_instance
        except Exception as e:
            logger.exception(f"Failed to initialize {model_key}.")
            raise