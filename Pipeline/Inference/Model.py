"""  
Model.py

- Class for handling model interaction via Gesellschaft für wissenschaftliche
Datenverarbeitung Göttingen (GWDG) ChatAI API 
- Chat AI documentation: https://docs.hpc.gwdg.de/services/chat-ai/
"""
import requests
from typing import List, Dict, Any
from langchain_openai import ChatOpenAI
from Utils.Logger import setup_logger

class ModelHandler:
    """ 
    Handles interactions with the GWDG ChatAI API, including retrieval of 
    available models and initialization of model instances with customizable
    configurations.

    :attr api_key: API key for authenticating requests to the model API.
    :attr base_url: Base URL for the model API endpoint.
    :attr logger: Logger instance. Defaults to a file-speicific logger.
    :attr available_models: List of models available through the API.
    :attr main_model: Main model selected for superior baseline performance.
    :attr base_models: A list of baseline models to be compared in the zeroshot setting.
    :attr default_configs: Default configuration parameters for model initialization.
    :attr _model_keys_cache: Stores the list of available model keys across class instances.
    """
    
    _model_keys_cache = None
    
    def __init__(self, api_key: str, base_url: str, logfile: str = "logs/ModelHandler.log"):
        self.logger = setup_logger(__name__, logfile)
        self.api_key = api_key
        self.base_url = base_url

        # Fetch available model keys if cache is emptys
        if ModelHandler._model_keys_cache is None:
            self.logger.info("Fetching available model keys for the first time.")
            ModelHandler._model_keys_cache = self.get_available_model_keys(self.base_url, self.api_key)
        self.available_models = ModelHandler._model_keys_cache

        self.main_models = ['llama-3.1-sauerkrautlm-70b-instruct', 'mistral-large-instruct', 'qwq-32b']
        self.base_models = ['meta-llama-3.1-8b-instruct',
                            'qwq-32b',
                            'deepseek-r1-distill-llama-70b',
                            'llama-3.3-70b-instruct',
                            'llama-3.1-sauerkrautlm-70b-instruct',
                            'mistral-large-instruct',
                            'qwen2.5-72b-instruct',
                            ]
        self.default_configs = {
            "timeout": 180, # seconds
            "max_retries": 2
        }
        
    def get_available_model_keys(self, base_url: str, api_key: str) -> List[str]:
        """Returns a list of available model keys from the API."""
        url = base_url + "/models"
        headers = {"Authorization": f"Bearer {api_key}"}
        response = requests.get(url, headers=headers)
        if response.status_code != 200:
            self.logger.error(f"Error fetching available model keys: {response.status_code}")
            response.raise_for_status()
        models = response.json()
        
        return [model_key["id"] for model_key in models["data"]]
    
    def initialize_model(self, model_key: str, custom_configs:  Dict[str, Any] = None) -> ChatOpenAI:
        """Returns an instance of an OpenAI model with customized configs, if any."""      
        self.logger.info(f"Initializing {model_key}")
        
        if model_key not in self.available_models:
            self.logger.error(f"Invalid model key. Available models: {self.available_models}")
            raise ValueError(f"Invalid model key: {model_key}")
        
        configs = {**self.default_configs, **(custom_configs or {})}
        
        try:
            model_instance = ChatOpenAI(
                api_key=self.api_key,
                base_url=self.base_url,
                model_name=model_key,
                **configs,
            )
            return model_instance
        except Exception as e:
            self.logger.exception(f"Failed to initialize {model_key}.")
            raise