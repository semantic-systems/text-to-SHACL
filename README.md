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

## File Structure

The repository is structured as follows.

- text-to-SHACL
    - **[data](data)**
        - **[raw](data/raw)**: Data downloaded on 2025-01-20, remote repository only includes exemplary files
            - **[service_catalogs](data/raw/service_catalogs)**: Catalogs listing administrative services by a given municiaplity
            - **[all_service_descriptions](data/raw/service_descriptions)**: Full descriptions of all adminsitrative services
            - **[social_benefit_requirements](data/raw/social_benefit_requirements)**: Name, idlb, and requirements text of social benfeits
        - **[processed](TODO)**:
            - **[shacl_gold](path/)**: Human-generated SHACL shapes.
            - **[splits](path/)**: Test and train split.
        - **[results](path/)**: Model output and evaluation metrics per experiment
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

    - **[Pipeline](path/to/src)**: Code used for generation and evaluation.
        - **[Generation](path/)**: Code for generating model output.
            - **[generator_classes](path/)**: Code for interacting with the LLM inlcuding prompt generation and server access.
                - [api_access.py](path/)
                - [gen_prompt.py](path/)
            - [run_generation.py](path/)
        - **[Evaluation](path/)**: Code for evaluating machine-generated SHACL shapes.
        - **[Prompt](path/)**
            - **[Instructions](path/)**: Instruction text per prompting method (.txt)
            - ontology.ttl: Context for prompting (.ttl)

    - **[Preprocessing](Preprocessing)**: Code for generating the dataset.
        - [ExtractSocialBenefitRequirements.py](Preprocessing/ExtractSocialBenefitRequirements.py): Select social benefits and extract eligibility requirements.
        - [GetServiceDescriptions.py](Preprocessing/GetServiceDescriptions.py): Download all administrative service descriptions.
        - [SplitDataset.py](Preprocessing/SplitDataset.py): Split data into test and train set.
    - **[ressources](resources)**: Additional resources used for modelling and validation.
        - **[requiremets_decomposition](resources/requirements_decomposition)**: Decomposition of requirements texts into individual requirements.
        - **[schemata](resources/schemata)**: Information about the data framework.
        - **[templates](resources/templates)**: Templates for SHACL graphs and requirements decomposition.
        - **[user_profiles](resources/user_profiles)**: Synthetic user profiles.
    - **[Utils](Utils)**: Utility functions organized by task.

## Data Source

TODO