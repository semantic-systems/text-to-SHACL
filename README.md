# text-to-SHACL

This repository contains the code for the Master's thesis **Text2SHACL: LLM-Driven Generation of Validation Graphs for Automatic Assessment of Social Benefit Eligibility**. The project explores how large language models (LLMs) can support the automatic generation of SHACL shapes graphs from natural language text, in particulr descriptions of eligibility requirements for social benefits.

## Author

**Name**: Seike Appold

**Email**: seike.appold@stud.leuphana.de

**Institution**: Leuphana University Lüneburg, Institute of Information Systems

**Program**: Management & Data Science

## Experiment Setups and Evaluation

Each experiment consists of prompting one or more LLM to generate SHACL shapes graphs from natural language eligibility requirements. They differ in the components included in the prompts:
- **Baseline**: Instruction + ontology + input text
- **Fewshot**: Instruction + ontology + selected worked examples + input text
- **Chain-of-Thought (CoT)**: Instruction + ontology + selected worked examples with intermediate reasoning steps + input text

The ontology specifies the classes, properties, and individuals used in the RDF data to be validated. When applicable, examples are selected based on input embedding similarity.

The generated shapes graphs are compared against expert-annotated gold graphs using two groups of metrics:
- **Syntactic quality**: Graph Edit Distance (GED), G-BERTScore, Triple Match (Precision, Recall, F1)
- **Semantic quality**: Comparison of validation outcomes on synthetic user profiles (Precsion, Recall, F1, Accuracy)

## Usage

### Installation

Run `pip install -r requirements.txt`

### Running an Experiment

To run an experiment with the default configurations from the thesis, run the following command from the root-directory, replacing the placeholders as specified below:

```bash
python Pipeline/Inference/RunInference.py   --mode <mode> \
                                            --api_key <api_key> \
                                            --base_url <base_url> \
```

| Parameter                 | Required | Description                                                                                        | Default                             |
| ------------------------- | -------- | -------------------------------------------------------------------------------------------------- | ----------------------------------- |
| `--mode`                  | ✅        | Prompting strategy: `baseline`, `fewshot`, or `cot` (chain-of-thought).                            | —                                   |
| `--api_key`               | ✅        | Your API key for the [Chat-AI API](https://docs.hpc.gwdg.de/services/saia/index.html#api-request) | —                                   |
| `--base_url`              | ✅        | Base URL for the Chat-AI API endpoint.                                                             | —                                   |
| `--num_examples`          | ❌        | Number of examples (`fewshot`/`cot` only)                       | `1` (`fewshot`/`cot`), `0` (`baseline`)                                 |
| `--k`                     | ❌        | Number of folds for k-fold cross-validation (`fewshot`/`cot` only). Must be at least 2.            | `3` (`fewshot`/`cot`), `0` (`baseline`)                                 |
| `--custom_models`         | ❌        | Space-separated list of model names to use. See [Chat-AI documentation](https://docs.hpc.gwdg.de/services/chat-ai/models/index.html) for available models.   | `None`                              |

**Note**: The script expects a standard directory structure for test inputs, prompt components, results, and gold data. You can override these: `--test_dir`, `--prompt_components_dir`, `--results_dir`, `--groundtruth_dir`

### Evaluating an Experiment

To compute the performance metrics specified above for a given experiment run, run the following command from the root-directory:
```bash
python Pipeline/Evaluation/RunEvaluation.py --experiment <experiment>
```

| Parameter                 | Required | Description                                                                                        | Default                             |
| ------------------------- | -------- | -------------------------------------------------------------------------------------------------- | ----------------------------------- |
| `--experiment`                  | ✅        | Name of the experiment to evaluate. Must match the name of the experiment folder.                           | —

**Note**: The script expects a standard directory structure for results, SHACL gold files, and user profiles. You can override these: `--results_dir`, `--shacl_gold_dir`, `--profiles_dir`

### Implementation Details

The experiments and evaluation were conducted using `Python 3.12.3` on `Ubuntu 24.04.2 LTS`, with model inference run on the HPC infrastructure provided by the [Gesellschaft für wissenschaftliche Datenverarbeitung mbH Göttingen](https://docs.hpc.gwdg.de/services/chat-ai/).

## Data Source

The dataset consists of two parts:

- **Requirements texts**: The natural language descriptions of eligibility requirements for social benefits were retrieved using the [Suchdienst-API](https://anbindung.pvog.cloud-bdc.dataport.de/api/suchdienst) from the [Portalverbund Online Gateway (PVOG)](https://anbindung.pvog.cloud-bdc.dataport.de/about-us). The data was downloaded on **January 20, 2025**. For the raw data, only exemplary files are included on remote.

- **SHACL Gold**: The shapes graphs used as ground truth in this project were generated by the author, and independently verified by two domain experts.

## File Structure

The repository is structured as follows.

- text-to-SHACL
    - **[Analysis](Analysis)**: Code and files for analyzing and visualization results.
    - **[data](data)**
        - **[processed](data/processed)**
            - **[requirements_texts](data/processed/shacl_gold)**: Input requirements texts for selected benefits.
            - **[shacl_gold](data/processed/requirements_texts)**: Human-annotated SHACL graphs (ground truth).
        - **[raw](data/raw)**
            - **[service_catalogs](data/raw/service_catalogs)**: All administrative services by municiaplity.
            - **[all_service_descriptions](data/raw/service_descriptions)**: Full descriptions of all adminsitrative services.
            - **[social_benefit_descriptions](data/raw/social_benefit_descriptions)**: Intermediate benefit selection.
    - **[Pipeline](Pipeline)**
        - **[Inference](Pipeline/Inference)**: Code for generating model output with different prompts.
        - **[Evaluation](Pipeline/Evaluation)**: Code for evaluating LLM-generated SHACL shapes.
    - **[Preprocessing](Preprocessing)**: Code for scraping and preparing the dataset.
    - **[resources](resources)**
        - **[requiremets_decomposition](resources/requirements_decomposition)**: Extracted individual requirements.
        - **[schemata](resources/schemata)**: Metadata about benefits, experiments, and SHACL vocabulary.
        - **[templates](resources/templates)**: SHACL & Decomposition templates.
        - **[user_profiles](resources/user_profiles)**: Synthetic usre profiles in RDF.
    - **[results](results)**: Model output and main syntactic and semantic evaluation metrics.
         - <run_id>/: One folder per experiment run (e.g., baseline_0ex0fcv_1745664019)
            - <model_name>/: One folder per model used in the run
                - metrics/: Evaluation metrics for this model
                - output/: Raw and parsed model outputs
                    - parsed_output/: Generated SHACL graphs per requirement
    - **[Utils](Utils)**: General helper functions used throughout the repository.


## Acknowledgments & Demo

Special thanks to [Ben](https://github.com/wbglaeser) and [Benjamin](github.com/benjaminaaron) from **Förderfunke** for supporting the annotation process with their practical expertise and providing the idea to use SHACL validation to assess social benefit eligibility, which inspired and shaped this project. A running demo of their system is available on their [website](https://foerderfunke.org/), and additional resources can be found on their [GitHub](https://github.com/Citizen-Knowledge-Graph).