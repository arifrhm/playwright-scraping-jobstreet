import csv
from playwright.sync_api import sync_playwright


def scrape_jobstreet_using_chrome_debug():
    # Open the browser and page using the existing session
    with sync_playwright() as p:
        browser = p.chromium.connect_over_cdp(
            "http://localhost:4444"
        )  # Connect to the existing browser session
        context = browser.contexts[0]
        page = context.pages[0] if context.pages else context.new_page()

        # List of job categories to scrape
        job_categories = [
            "backend-jobs",
            "dataengineer-jobs",
            "frontend-jobs",
            "datascientist-jobs",
            "fullstack-jobs",
            "devops-jobs",
            "cybersecurity-jobs",
            "programmer-jobs",
            "software-jobs",
        ]
        # Instead of just waiting for a selector,
        # also wait for the network to be idle
        # Wait for network to be idle (page load is complete)
        page.wait_for_load_state("networkidle")
        # Wait for job listings to appear
        page.wait_for_selector('div[data-search-sol-meta]', timeout=15000)

        # Open the CSV file for writing
        with open(
                "job_listings.csv",
                mode="w",
                newline="",
                encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["Job Title", "Company", "Job Link"])  # CSV header

            # Loop through each job category
            for category in job_categories:
                url = f"https://id.jobstreet.com/id/{category}"
                print(f"Scraping jobs from: {url}")
                page.goto(url)

                # Wait for the job cards to load
                # Updated selector
                page.wait_for_selector('div[data-search-sol-meta]')

                # Scrape the job listings for this category
                while True:  # Loop to scrape multiple pages
                    # Get all job cards from the page
                    # using the updated selector
                    job_listings = page.query_selector_all(
                        'div[data-search-sol-meta]'  # Updated selector
                    )

                    for job in job_listings:
                        # Get the job link from the <a> tag inside the job card
                        job_link = job.query_selector(
                            'a[data-automation="jobTitle"]'
                            )
                        job_link = (
                            job_link.get_attribute("href")
                            if job_link else "No Link"
                        )

                        # Get the job title
                        job_title = (
                            job.query_selector(
                                'a[data-automation="jobTitle"]'
                            ).inner_text()
                            if job.query_selector(
                                'a[data-automation="jobTitle"]'
                                )
                            else "No Title"
                        )

                        print("Job Title:", job_title)

                        # Get the company name
                        company = (
                            job.query_selector(
                                'a[data-automation="jobCompany"]'
                            ).inner_text()
                            if job.query_selector(
                                'a[data-automation="jobCompany"]'
                                )
                            else "No Company"
                        )

                        # Write the job data to CSV
                        writer.writerow([job_title, company, job_link])

                    # Check if the next_button JSHandle is not None
                    next_button = page.query_selector(
                        'a[aria-label="Selanjutnya"]'
                        )

                    if next_button:
                        # Check if the "Next" button is
                        # hidden (aria-hidden="true")
                        aria_hidden = next_button.get_attribute("aria-hidden")

                        if aria_hidden == "true":
                            print("No more pages, 'Next' button is hidden.")
                            # Exit loop if 'Next' button is
                            # hidden (no more pages)
                            break

                        # Check if the "Next" button is enabled (clickable)
                        if next_button.is_enabled():
                            page_number = next_button.get_attribute(
                                "data-automation"
                                )
                            print(f"Moving to next page... {page_number}")
                            next_button.click()
                            page.wait_for_load_state(
                                "networkidle"
                            )  # Wait for the next page to load
                        else:
                            print(
                                "No more pages, or 'Next' button is disabled."
                                )
                            # Exit loop if the button is disabled or
                            # no more pages
                            break
                    else:
                        print("No more pages, 'Next' button not found.")
                        # Exit loop if 'Next' button is not present
                        break


# Run the function to scrape job data and save it to CSV
scrape_jobstreet_using_chrome_debug()
