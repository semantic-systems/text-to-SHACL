# text-to-SHACL

This repository contains the code for my Master's thesis **Without Title**. The project explores how LLMs can support the automatic generation of SHACL shapes from natural language text.

## Author

**Name**: Seike Appold
**Email**: seike.appold@stud.leuphana.de
**Institution**: Leuphana University Lüneburg, Institute of Information Systems
**Program**: Management & Data Science

## Repo Structure

├── scraping/
    ├── data/
        ├── ars/
            ├── ars_clean.csv
            ├── ars_raw.csv
        ├── services/
            ├── ars_010010000000.csv
            ├── ...
            ├── unique_idlbs.csv
    ├── code/
        ├── a_extract_ars.py
        ├── b_extract_idlbs.py
        ├── c_extract_eligibility_requirements.py
    ├── inspection.ipynb