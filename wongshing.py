import pandas as pd
import requests
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np

# Load the Excel file into a DataFrame
file_path = "jobs.xlsx"
df = pd.read_excel(file_path)

# Function to scrape data for a given job ID
def scrape_job(job_id):
    try:
        # Menggunakan 'id' untuk membentuk URL
        url = f"https://id.jobstreet.com/id/job/{job_id}"
        response = requests.get(url)
        if response.status_code == 200:
            # Parse the HTML using BeautifulSoup
            soup = BeautifulSoup(response.text, 'html.parser')
            # Find the job details by the given selector
            job_details_div = soup.select_one('div[data-automation="jobAdDetails"]')
            if job_details_div:
                job_description = job_details_div.get_text(strip=True)
                print(f"Successfully scraped data for job ID: {job_id}")
                return {"job_id": job_id, "description": job_description}
            else:
                print(f"Job details not found for job ID: {job_id}")
        else:
            print(f"Failed to scrape data for job ID: {job_id}, Status Code: {response.status_code}")
    except requests.RequestException as e:
        print(f"Error scraping data for job ID: {job_id}, Error: {e}")

# Extract all job IDs from the DataFrame
job_ids = df['id'].dropna().unique()  # Assuming 'id' column exists in the DataFrame

# Open the JSON file in write mode and write the opening of the list
output_file = "scraped_data_by_id.json"
with open(output_file, "w", encoding="utf-8") as json_file:
    json_file.write("[\n")

# Use ThreadPoolExecutor to scrape URLs in parallel and write results in real-time
with ThreadPoolExecutor(max_workers=5) as executor:
    future_to_job_id = {executor.submit(scrape_job, job_id): job_id for job_id in job_ids}
    is_first_result = True  # Flag to handle comma separation for JSON elements
    with open(output_file, "a", encoding="utf-8") as json_file:
        for future in as_completed(future_to_job_id):
            job_id = future_to_job_id[future]
            try:
                result = future.result()  # Block until the individual thread completes
                if result:
                    # Write the result to the JSON file
                    if not is_first_result:
                        json_file.write(",\n")  # Add a comma before every new element except the first
                    json.dump(result, json_file, ensure_ascii=False, indent=4, default=lambda o: int(o) if isinstance(o, np.int64) else o)
                    is_first_result = False  # Set to False after the first result is written
            except Exception as e:
                print(f"An error occurred while scraping job ID {job_id}: {e}")

# Write the closing bracket of the list
with open(output_file, "a", encoding="utf-8") as json_file:
    json_file.write("\n]\n")

print(f"Scraped data has been written to {output_file}")
