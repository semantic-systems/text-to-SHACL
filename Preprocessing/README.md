# Usage

To recreate the input data, run the following scripts **in order**. If you do not specify the optional parameters, they will default to the values used for this project.

```bash
# Step 1: Save ARS from codelists to file with ID schemata
python Preprocessing/GetARS.py <save_dir_codelists> <ids_schema_path> --municipality_codelist_url --state_codelist_url

# Step 2: Download detailed descriptions for all administrative services provided by the PVOG
python Preprocessing/GetServiceDescriptions.py <service_catalogs_dir> <all_service_descriptions_dir> <ids_schema_path> --service_catalog_url --service_desc_url

# Step 3: Select social benefits for further analysis and filter descriptions
python Preprocessing/ExtractSocialBenefitRequirements.py <all_service_descriptions_dir> <social_benefits_dir> --editorial_system <editorial_system> --matters --addressees --legal_bases --manual_selection

# Step 4: Split the data into train and test sets
python Preprocessing/SplitDataset.py <social_benefits_dir> <splits_dir> --train_ratio

# Step 5: Get the mappings used in further analysis
python Preprocessing/GetMappings.py <service_desc_dir> <schemata_dir>
```

