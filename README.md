# text-to-SHACL

This repository contains the code for my Master's thesis **Without Title**. The project explores how LLMs can support the automatic generation of SHACL shapes from natural language text.

## Author

**Name**: Seike Appold

**Email**: seike.appold@stud.leuphana.de

**Institution**: Leuphana University Lüneburg, Institute of Information Systems

**Program**: Management & Data Science

## Project Structure

- **`/data`**
  - **`/processed`**: CSV files with relevant information extracted from raw data.
    - **`/all_administrative_services.csv`**: Name, description, ID-LB, ARS, eligibility requirements and legal bases for all administrative services, where multiple legal bases are separated according to the following format: "Label1<>URL1 || Label2<>URL2 || ..."
    - **`/federal_social_services.csv`**: Subset of all_services.csv that contains only federal social services.
    - **`/municipalities.csv`**: All ARS with corresponding municiaplity.
    - **`/unique_idlbs.csv`**: All unique ID-LBs with one corresponding ARS.
  - **`/raw`** (untracked): Data prior to processing.
    - **`/ars`**: Excel with all ARS and corresponding municipality.
    - **`/service_catalogs`**: For each ars, csv listing all administrative services.
    - **`/service_descriptions_all`**: For each unique ID-LB, the complete servie descripition in JSON.
    - **`/service_descriptions_social`**: For federal social services, the complete service description in JSON.
  - **`scrapting_scripts`**: Contains the code used to scrape the data from the web.
- **`/evaluation`**: Pipeline for evaluating machine-generated SHACL shapes graphs.
- **`/generation`**: Pipeline for generating SHACL shapes graphs from text using LLMs.
- **`/knowledge_graph`**:
    - **`/ontology`**: Conceptualization of personal information relevant to determine whether an individual may be elgibile for a social service or not.
    - **`/shacl_gold`**: Human-generated SHACL shapes.
    - **`/user_profiles`**: Synthetic personal information for testing SHACL shapes.

Dataset Todos:
- Clean integration of e_federal_social_services
- Remove old versions of files
- Command line arguments for file paths and save paths instead of hard-coded
- Extract only Name, ID-LB, Short Description and Prerequisites

Modelling Todos:
- Generate 2 more shapes
- Evaluate the shapes with (1) syntax validator, (2) sample user profiles