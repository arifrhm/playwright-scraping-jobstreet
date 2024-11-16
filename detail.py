import asyncio
import certifi
import ssl
import aiohttp
import pandas as pd
from bs4 import BeautifulSoup
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)
ssl_context = ssl.create_default_context(cafile=certifi.where())


async def fetch(session, url):
    print("Getting data from : " + url)
    async with session.get(url, ssl=ssl_context) as response:
        return await response.text()


async def parse_job_details(html, url):
    soup = BeautifulSoup(html, "html.parser")
    details = {}

    # Mengekstrak detail pekerjaan
    # Catatan: selector ini mungkin perlu
    # disesuaikan tergantung pada struktur HTML JobStreet
    title_elem = soup.select_one('[data-automation="job-detail-title"]')
    details["title"] = title_elem.text.strip() if title_elem else "N/A"

    company_elem = soup.select_one(
        '[data-automation="advertiser-name"]'
    )
    details["company"] = company_elem.text.strip() if company_elem else "N/A"

    details["link"] = url

    details["description"] = soup.select_one(
        'div[data-automation="jobAdDetails"]'
    )
    salary_elem = soup.select_one('[data-automation="job-detail-salary"]')
    details['salary'] = salary_elem.text.strip() if salary_elem else "N/A"

    location_elem = soup.select_one(
        '[data-automation="job-detail-location"]'
        )
    details['location'] = location_elem.text.strip()\
        if location_elem else "N/A"

    return details


async def get_job_details(session, url):
    html = await fetch(session, url)
    return await parse_job_details(html, url)


async def worker(session, input_queue, output_queue):
    while True:
        job = await input_queue.get()
        if job is None:
            break
        try:
            url = "https://id.jobstreet.com" + job['Job Link']
            details = await get_job_details(session, url)
            job.update(details)
            await output_queue.put(job)
        except Exception as e:
            print(f"Error getting details for {url}: {e}")
        finally:
            input_queue.task_done()


async def main():
    input_queue = asyncio.Queue()
    output_queue = asyncio.Queue()

    # Membaca file CSV menggunakan pandas
    df = pd.read_csv('job_listings.csv')
    for _, row in df.iterrows():
        await input_queue.put(row.to_dict())

    async with aiohttp.ClientSession() as session:
        # Membuat worker tasks
        worker_tasks = []
        for _ in range(5):  # Menggunakan 5 worker
            task = asyncio.create_task(worker(
                session, input_queue, output_queue))
            worker_tasks.append(task)

        # Menunggu semua job selesai diproses
        await input_queue.join()

        # Memberi sinyal kepada worker untuk berhenti
        for _ in range(5):
            await input_queue.put(None)

        # Menunggu semua worker selesai
        await asyncio.gather(*worker_tasks)

    # Mengumpulkan hasil
    results = []
    while not output_queue.empty():
        results.append(await output_queue.get())

    # Membuat DataFrame dari hasil dan menyimpan ke CSV
    result_df = pd.DataFrame(results)
    result_df.to_csv('jobs_with_details.csv', index=False)
    logger.info("Finished processing. Results saved to jobs_with_details.csv")


if __name__ == "__main__":
    asyncio.run(main())
