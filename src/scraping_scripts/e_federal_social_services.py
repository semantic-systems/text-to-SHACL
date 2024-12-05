import os
import csv
from d_requirement_profiles_data import save_reqs_to_csv

# From social_services.csv, generate CSV that only contains services where ID-LB starts with "B"
save_dir_in = "scraping/data/processed"
filename_in = "social_services.csv"

federal_social_services = []
with open(os.path.join(save_dir_in, filename_in), 'r') as file:
    reader = csv.DictReader(file)
    for row in reader:
        if row["ID-LB"].startswith("B"):
            federal_social_services.append(row)
save_dir_out = "scraping/data/processed"
filename_out = os.path.join("federal_social_services.csv")
save_reqs_to_csv(federal_social_services, save_dir_out, filename_out)