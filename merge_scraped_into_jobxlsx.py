import pandas as pd
import json

# File paths
excel_file_path = "jobs.xlsx"
json_file_path = "scraped_data_by_id.json"
output_excel_file_path = "jobs_with_descriptions.xlsx"

# Load the Excel file into a DataFrame
df = pd.read_excel(excel_file_path)

# Load the JSON file into a list of dictionaries
with open(json_file_path, "r", encoding="utf-8") as json_file:
    scraped_data = json.load(json_file)

# Convert the list of dictionaries into a DataFrame
scraped_df = pd.DataFrame(scraped_data)

# Merge the original DataFrame with the scraped DataFrame on 'id'
# Assuming 'id' in df matches 'job_id' in scraped_df
df = df.merge(scraped_df, left_on='id', right_on='job_id', how='left')

# Drop 'job_id' column as it is a duplicate of 'id' now
df.drop(columns=['job_id'], inplace=True)

# Save the updated DataFrame to a new Excel file
df.to_excel(output_excel_file_path, index=False)

print(f"Updated Excel file has been saved to {output_excel_file_path}")
