import json
import os
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.common.by import By
import requests
from selenium.webdriver.support.ui import WebDriverWait


def scrape_jobstreet_api():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    caps = DesiredCapabilities.CHROME.copy()
    caps["goog:loggingPrefs"] = {
        "performance": "ALL"
    }  # Enable performance logs to capture network requests

    # Use 'desired_capabilities' in ChromeOptions instead of
    # passing it directly to webdriver.Remote
    options.set_capability("goog:loggingPrefs", {"performance": "ALL"})

    driver = webdriver.Remote(
        command_executor="http://85.31.232.226:4444/wd/hub", options=options
    )

    # List of job keywords to scrape
    job_keywords = [
        # "backend",
        "dataengineer",
        "frontend",
        "datascientist",
        "fullstack",
        "devops",
        "cybersecurity",
        "programmer",
        "software",
    ]

    # Create directory to save JSON files if it doesn't exist
    if not os.path.exists("job_data"):
        os.makedirs("job_data")

    # Loop through each job keyword
    for keyword in job_keywords:
        page_number = 1
        while True:
            # Construct the URL for the job listings page if it's the first page
            if page_number == 1:
                url = f"https://id.jobstreet.com/id/{keyword}-jobs"
                print(f"Scraping jobs for keyword '{keyword}' on page {page_number}")
                driver.get(url)
            else:
                print(f"Scraping jobs for keyword '{keyword}' on page {page_number}")

            # Wait for the page to load completely
            try:
                WebDriverWait(driver, 20).until(
                    lambda d: d.execute_script("return document.readyState")
                    == "complete"
                )
            except Exception as e:
                print(f"Error waiting for page to load: {e}")

            # Extract network requests for API responses from performance logs
            logs = driver.get_log("performance")
            xhr_requests = []
            for log in logs:
                try:
                    log_data = json.loads(log["message"])
                    message = log_data["message"]
                    # Filter only Fetch/XHR requests
                    if message["method"] == "Network.responseReceived" and message[
                        "params"
                    ]["type"] in ["XHR", "Fetch"]:
                        url = message["params"]["response"]["url"]
                        if "counts" in url:
                            modified_url = url.replace("counts", "search")
                            response = requests.get(modified_url)
                            if response.status_code == 200:
                                # Save the response literally without any processing
                                with open(
                                    f"job_data/{keyword}_page_{page_number}_modified.json",
                                    "w",
                                    encoding="utf-8",
                                ) as mod_file:
                                    json.dump(
                                        response.json(),
                                        mod_file,
                                        ensure_ascii=False,
                                        indent=4,
                                    )
                                print(
                                    f"Saved modified response for keyword '{keyword}' page {page_number}"
                                )
                        xhr_requests.append(
                            log_data
                        )  # Save only Fetch/XHR related logs
                except Exception as e:
                    continue

            # Save all XHR/Fetch network requests to a JSON file for debugging
            with open(
                f"job_data/{keyword}_page_{page_number}_requests.json",
                "w",
                encoding="utf-8",
            ) as req_file:
                json.dump(xhr_requests, req_file, ensure_ascii=False, indent=4)

            next_button = driver.find_element(
                By.CSS_SELECTOR, '[aria-label="Selanjutnya"]'
            )

            print(next_button.text)
            print(next_button.get_attribute("aria-hidden"))
            if next_button and next_button.get_attribute("aria-hidden") == "false":
                driver.execute_script("arguments[0].scrollIntoView(true);", next_button)
                next_button.click()
                page_number += 1
                print(f"Scraping already on page {page_number}")
            else:
                print("No more pages, 'Next' button is not enabled.")
                break

    # Quit the WebDriver
    driver.quit()


# Run the function to scrape job data and save it as JSON files
scrape_jobstreet_api()
