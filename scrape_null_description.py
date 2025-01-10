import pandas as pd
import requests
import json
from bs4 import BeautifulSoup
from concurrent.futures import ThreadPoolExecutor, as_completed

# File paths
excel_file_path = "jobs_with_descriptions.xlsx"
output_excel_file_path = "jobs_with_descriptions_updated.xlsx"
success_log_path = "success_log.json"
failure_log_path = "failure_log.json"

# Load the Excel file into a DataFrame
df = pd.read_excel(excel_file_path)

# Filter the rows where 'description' is NaN (missing)
missing_description_df = df[df["description"].isna()]

# Get the job IDs for the rows where the description is missing
job_ids_to_scrape = missing_description_df["id"].dropna().unique()

# Open the log files in append mode
with open(success_log_path, "w", encoding="utf-8") as success_file:
    success_file.write("[\n")  # Begin JSON array
with open(failure_log_path, "w", encoding="utf-8") as failure_file:
    failure_file.write("[\n")  # Begin JSON array


# Function to scrape data for a given job ID
def scrape_job(job_id):
    try:
        # Menggunakan 'id' untuk membentuk URL
        url = f"https://id.jobstreet.com/id/job/{job_id}"
        response = requests.get(url)
        if response.status_code == 200:
            # Parse the HTML using BeautifulSoup
            soup = BeautifulSoup(response.text, "html.parser")
            # Find the job details by the given selector
            job_details_div = soup.select_one(
                'div[data-automation="jobAdDetails"]'
            )
            if job_details_div:
                job_description = job_details_div.get_text(strip=True)
                print(f"Successfully scraped data for job ID: {job_id}")

                # Write success log to file in real-time
                with open(
                    success_log_path,
                    "a",
                    encoding="utf-8",
                ) as success_file:
                    json.dump(
                        {"job_id": job_id, "description": job_description},
                        success_file,
                        ensure_ascii=False,
                        indent=4,
                    )
                    success_file.write(",\n")

                return {"job_id": job_id, "description": job_description}
            else:
                error_message = f"Job details not found for job ID: {job_id}"
                print(error_message)

                # Write failure log to file in real-time
                with open(
                    failure_log_path,
                    "a",
                    encoding="utf-8"
                ) as failure_file:
                    json.dump(
                        {"job_id": job_id, "error": "Job details not found"},
                        failure_file,
                        ensure_ascii=False,
                        indent=4,
                    )
                    failure_file.write(",\n")

        else:
            error_message = f"Failed to scrape data for job ID: {job_id}, "
            error_message += f"Status Code: {response.status_code}"
            print(error_message)

            # Write failure log to file in real-time
            with open(failure_log_path, "a", encoding="utf-8") as failure_file:
                json.dump(
                    {"job_id": job_id,
                     "error": f"Status Code: {response.status_code}"},
                    failure_file,
                    ensure_ascii=False,
                    indent=4,
                )
                failure_file.write(",\n")

    except requests.RequestException as e:
        error_message = f"Error scraping data for job ID: {job_id}, Error: {e}"
        print(error_message)

        # Write failure log to file in real-time
        with open(failure_log_path, "a", encoding="utf-8") as failure_file:
            json.dump(
                {"job_id": job_id, "error": str(e)},
                failure_file,
                ensure_ascii=False,
                indent=4,
            )
            failure_file.write(",\n")


# Use ThreadPoolExecutor to scrape URLs in parallel
scraped_results = []
with ThreadPoolExecutor(max_workers=5) as executor:
    future_to_job_id = {
        executor.submit(
            scrape_job, job_id
        ): job_id for job_id in job_ids_to_scrape
    }
    for future in as_completed(future_to_job_id):
        job_id = future_to_job_id[future]
        try:
            # Block until the individual thread completes
            result = future.result()
            if result:
                scraped_results.append(result)
        except Exception as e:
            error_message = \
                f"An error occurred while scraping job ID {job_id}: {e}"
            print(error_message)
            # Write failure log to file in real-time
            with open(failure_log_path, "a", encoding="utf-8") as failure_file:
                json.dump(
                    {"job_id": job_id, "error": str(e)},
                    failure_file,
                    ensure_ascii=False,
                    indent=4,
                )
                failure_file.write(",\n")

# Convert scraped results into a DataFrame
if scraped_results:
    scraped_df = pd.DataFrame(scraped_results)

    # Update the original DataFrame with the new descriptions
    df = df.set_index("id")  # Set 'id' as the index for easier updating
    scraped_df = scraped_df.set_index(
        "job_id"
    )  # Set 'job_id' as the index to match with df's 'id'

    # Update only the missing descriptions
    df.update(scraped_df)

    # Reset index to make 'id' a normal column again
    df.reset_index(inplace=True)

    # Save the updated DataFrame to a new Excel file
    df.to_excel(output_excel_file_path, index=False)
    print(
        "Updated Excel file with scraped descriptions"
        f"has been saved to {output_excel_file_path}"
    )
else:
    print("No new descriptions were scraped.")

# Close JSON arrays in log files
with open(success_log_path, "a", encoding="utf-8") as success_file:
    success_file.write("\n]\n")

with open(failure_log_path, "a", encoding="utf-8") as failure_file:
    failure_file.write("\n]\n")

print(f"Success log has been saved to {success_log_path}")
print(f"Failure log has been saved to {failure_log_path}")
