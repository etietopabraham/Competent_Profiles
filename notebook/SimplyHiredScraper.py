import cloudscraper
from bs4 import BeautifulSoup
import pandas as pd
import random
from urllib.parse import quote_plus, urlparse, ParseResult
import math
import time
import concurrent.futures

class SimplyHiredJobScraper:
    def __init__(self, job_roles, locations):
        self.job_roles = job_roles
        self.locations = locations
        self.base_url = "https://www.simplyhired.ca"

    @staticmethod
    def get_headers():
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
            "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:54.0) Gecko/20100101 Firefox/54.0",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/79.0.3945.88 Safari/537.36",
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:72.0) Gecko/20100101 Firefox/72.0"
        ]

        headers = {
            "Connection": "keep-alive",
            "Cache-Control": "max-age=0",
            "Upgrade-Insecure-Requests": "1",
            "User-Agent": random.choice(user_agents),
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Sec-Fetch-Site": "none",
            "Sec-Fetch-Mode": "navigate",
            "Sec-Fetch-User": "?1",
            "Sec-Fetch-Dest": "document",
            "Accept-Encoding": "gzip, deflate, br",
            "Accept-Language": "en-GB,en-US;q=0.9,en;q=0.8",
        }

        return headers

    def scrape_jobs(self, job_role, location):
        # Encode job_search for URL (replace spaces with '+' and other special characters)
        job_role_encoded = quote_plus(job_role)

        # Encode location
        location_encoded = quote_plus(location)

        # Construct URL with search query
        url = f"{self.base_url}/search?q={job_role_encoded}&l={location_encoded}"

        # Create a scraper instance
        scraper = cloudscraper.create_scraper()
        
        # Make an HTTP GET request to the URL
        response = scraper.get(url, headers=self.get_headers())

        # Check status code
        if response.status_code != 200:
            print(f"Request to {url} failed with status code {response.status_code}.")
            return

        # Parse the HTML content of the page with BeautifulSoup
        soup = BeautifulSoup(response.text, "html.parser")

        # Find total job count and calculate the number of pages to scrape
        try:
            total_job_count = int(soup.find('span', {'class': 'posting-total'}).text)
            job_pages = math.ceil(total_job_count/20)
        except Exception as e:
            print(f"Failed to extract total job count: {e}")
            return

        # Loop through all pages
        for page in range(1, job_pages + 1):
            # Print the page number
            print(f"Scraping page {page}...")

            # Sleep for 3 seconds between requests to avoid being blocked
            time.sleep(random.uniform(3, 6))

            # If it's not the first page, make another request and parse it
            if page > 1:
                url = f"{self.base_url}/search?q={job_role_encoded}&l={location_encoded}&pn={page}"
                response = scraper.get(url, headers=self.get_headers())

                # Check status code
                if response.status_code != 200:
                    print(f"Request to {url} failed with status code {response.status_code}.")
                    continue

                soup = BeautifulSoup(response.text, "html.parser")

            # Find the list of jobs on the page
            job_list = soup.find('ul', {'class': 'jobs'})
            jobs  = job_list.findAll('div', {'class': 'SerpJob-jobCard'})

            # Loop through all jobs on the page
            for job in jobs:
                # Extract job details and construct job URL
                title_tag = job.find('h3', {'class': 'jobposting-title'})
                title = title_tag.text
                link = title_tag.find('a').attrs['data-mdref']
                
                # Remove query parameters from the job URL
                parsed_link = urlparse(link)
                link = ParseResult(scheme=parsed_link.scheme, netloc=parsed_link.netloc, 
                                path=parsed_link.path, params=parsed_link.params, 
                                query='', fragment=parsed_link.fragment).geturl()

                # Extract other job details
                company_name = job.find('span', {'class': 'jobposting-company'}).text
                job_location = job.find('span', {'class': 'jobposting-location'}).text
                job_summary = job.find('p', {'class': 'jobposting-snippet'}).text
                date_of_job_post = job.find('time').attrs['datetime']
                url = f"https://www.simplyhired.ca{link}?isp=0&q={job_role}"

                # Store job details in a dictionary and append it to our list
                data = {
                    'date_of_job_post': date_of_job_post,
                    'title':  title,
                    'job_location': job_location,
                    'company_name': company_name,
                    'job_link': url,
                    'job_summary': job_summary
                }

                yield data

    def get_job_details(self, job_url):
        """
        This function takes in a URL of a job posting, fetches the page,
        and extracts additional details like job type, qualifications, and description.
        """
        # Create a new scraper for each job detail page
        scraper = cloudscraper.create_scraper()
        response = scraper.get(job_url, headers=self.get_headers())
        soup = BeautifulSoup(response.text, "html.parser")

        # Extract additional info, like job description, job type, qualifications, etc.
        job_details = soup.find('div', {'class': 'viewjob-content'})

        # Job type
        job_type_tag = job_details.find('span', {'class': 'viewjob-jobType'})
        job_type = job_type_tag.text if job_type_tag else None

        # Job qualifications
        qualifications_tags = job_details.findAll('li', {'class': 'viewjob-qualification'})
        job_qualifications = [qual_tag.text for qual_tag in qualifications_tags] if qualifications_tags else None

        # Job description
        job_description_tag = job_details.find('div', {'data-testid': 'VJ-section-content-jobDescription'})
        job_description = job_description_tag.text if job_description_tag else None

        return {
            'job_type': job_type,
            'job_qualifications': job_qualifications,
            'job_description': job_description
        }
    
    def run(self):
        all_jobs_data = []
        for job_role in self.job_roles:
            for location in self.locations:
                print(f"Starting to scrape jobs for the role {job_role} in {location}...")
                job_data_generator = self.scrape_jobs(job_role, location)
                jobs_df = pd.DataFrame(job_data_generator)
                all_jobs_data.append(jobs_df)

        # Concatenate all dataframes
        all_jobs_df = pd.concat(all_jobs_data, ignore_index=True)

        # Use ThreadPoolExecutor to parallelize the fetching of job details
        with concurrent.futures.ThreadPoolExecutor() as executor:
            # Fetch job details for each job link
            job_details_list = list(executor.map(self.get_job_details, all_jobs_df['job_link'].tolist()))

        # Create a DataFrame from the list of job details
        jobs_details_df = pd.DataFrame(job_details_list)

        # Combine the original DataFrame with the job details DataFrame
        jobs_df = pd.concat([all_jobs_df, jobs_details_df], axis=1)

        return jobs_df
    

if __name__ == "__main__":
    # Define the job roles and locations to scrape
    job_roles = ["Machine Learning Engineer"]
    locations = ["Calgary, AB"]

    # Create a SimplyHiredJobScraper instance
    scraper = SimplyHiredJobScraper(job_roles, locations)

    # Run the scraper
    jobs_df = scraper.run()

    # Save the data to a CSV file
    jobs_df.to_csv("/Users/mac/Eti/CompetentPro/Competent_Profiles/notebook/data/jobs_data_simply_hired_calgary_ml_engineer.csv", index=False)    


