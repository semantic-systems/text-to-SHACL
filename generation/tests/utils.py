import requests
import json

# API configuration
BASE_URL = "https://chat-ai.academiccloud.de/v1"
def get_all_models(api_key):
    url = BASE_URL + "/models"
    headers = {
        "Authorization": f"Bearer {api_key}"
    }

    response = requests.get(url, headers=headers)

    if response.status_code == 200:
        # extract a list of model ids
        models = response.json()
        available_models = [model["id"] for model in models["data"]]

        return available_models
    else:
        response.raise_for_status()