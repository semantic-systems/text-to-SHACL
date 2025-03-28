# text-to-SHACL

This repository contains the code for my Master's thesis **Without Title**. The project explores how LLMs can support the automatic generation of SHACL shapes from natural language text.

## Author

**Name**: Seike Appold

**Email**: seike.appold@stud.leuphana.de

**Institution**: Leuphana University Lüneburg, Institute of Information Systems

**Program**: Management & Data Science

## An Example

TODO

## Usage

TODO

## Data Source

TODO

Data downloaded on 2025-01-20, remote repository only includes exemplary files

## Frameworks

TODO

## File Structure

The repository is structured as follows.

- text-to-SHACL
    - **[data](data)**
        - **[raw](data/raw)**: Unprocessed and intermediate data.
            - **[service_catalogs](data/raw/service_catalogs)**: Lists of all administrative services by municiaplity.
            - **[all_service_descriptions](data/raw/service_descriptions)**: Full descriptions of all adminsitrative services.
            - **[social_benefit_descriptions](data/raw/social_benefit_descriptions)**: Intermediate benefit selection.
        - **[processed](data/processed)**: Processed data prepared for experiments.
            - **[shacl_gold](data/processed/requirements_texts)**: Human-generated SHACL shapes graphs.
            - **[requirements_texts](data/processed/shacl_gold)**: Requirements texts for selected social benefits.
    - **[Pipeline](Pipeline)**: Code used to run experiments.
        - **[Inference](Pipeline/Inference)**: Code for generating model output.
        - **[Evaluation](Pipeline/Evaluation)**: Code for evaluating LLM-generated SHACL shapes.
    - **[Preprocessing](Preprocessing)**: Code for scraping and preparing the dataset. Please refer to the README.py inside this folder for usage.
    - **[resources](resources)**: Supporting materials.
        - **[requiremets_decomposition](resources/requirements_decomposition)**: Extraction and categorization of individual requirements from original texts.
        - **[schemata](resources/schemata)**: Metadata about social benefits and experiments.
        - **[templates](resources/templates)**: Templates for SHACL shapes graph and requirements decomposition.
        - **[user_profiles](resources/user_profiles)**: Synthetic user profiles.
    - **[results](path/)**: Model output and evaluation metrics per experiment.
        - **[baseline](path/)**
            - **[model1](path/)**
                - **[output](path/)**
                - **[metrics](path/)**
            - **[model2](path/)**
                -...
        - **[oneshot](path/)**
            - **[output](path/)**
            - **[metrics](path/)**
        - ...
    - **[Utils](Utils)**: Utility functions used throughout the repository.