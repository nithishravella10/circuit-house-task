import time
import json
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from bs4 import BeautifulSoup
from supabase import create_client, Client
import logging

class LetterboxdScraper:
    def __init__(self, supabase_url, supabase_key):
        """
        Initialize Supabase client and WebDriver
        """
        # Configure logging
        logging.basicConfig(level=logging.INFO, 
                            format='%(asctime)s - %(levelname)s: %(message)s')
        self.logger = logging.getLogger(__name__)
        
        # Supabase configuration
        self.supabase: Client = create_client(supabase_url, supabase_key)
        
        # Configure Chrome WebDriver
        options = Options()
        options.add_argument("--headless")
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
        self.driver = webdriver.Chrome(options=options)

    def scrape_single_page(self, url):
        """
        Scrape a single page of Tamil movies from Letterboxd
        """
        try:
            # Navigate to the URL and wait for content to load
            self.driver.get(url)
            WebDriverWait(self.driver, 10).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "poster-container"))
            )

            # Parse the page source
            soup = BeautifulSoup(self.driver.page_source, "html.parser")

            # Extract movie details
            movies = []
            for li in soup.find_all("li", class_="poster-container"):
                film_poster = li.find("div", class_="film-poster")
                if not film_poster:
                    continue

                # Extract and process movie data
                film_id = film_poster.get("data-film-id")
                film_name = film_poster.get("data-film-name")
                film_slug = film_poster.get("data-film-slug")
                release_year_str = film_poster.get("data-film-release-year")

                # Validate and process data
                movie_data = {
                    "data-film-id": int(film_id) if film_id and film_id.isdigit() else None,
                    "data-film-name": film_name,
                    "data-film-slug": film_slug or "",
                    "data-film-release-year": int(release_year_str) if release_year_str and release_year_str.isdigit() else None,
                    "data-film-link": f"https://letterboxd.com/film/{film_slug}" 
                        if film_slug else None
                }

                movies.append(movie_data)

            return movies
        
        except Exception as e:
            self.logger.error(f"Error scraping page {url}: {e}")
            return []

    def push_to_supabase(self, movies):
        """
        Push scraped movies to Supabase, handling each record individually
        """
        if not movies:
            self.logger.warning("No movies to insert")
            return

        # Track successful and failed insertions
        successful_insertions = 0
        failed_insertions = 0

        for movie in movies:
            try:
                # Insert or ignore if duplicate
                response = (
                    self.supabase.table("tamil-movies-info")
                    .upsert(movie, on_conflict="data-film-id")
                    .execute()
                )
                successful_insertions += 1
            except Exception as e:
                failed_insertions += 1
                self.logger.error(f"Error inserting movie: {movie}")
                self.logger.error(f"Insertion error details: {e}")
                continue

        # Log overall insertion summary
        self.logger.info(f"Page insertion summary - "
                         f"Successful: {successful_insertions}, "
                         f"Failed: {failed_insertions}")

    def scrape_multiple_pages(self, start_page, end_page):
        """
        Scrape multiple pages of Tamil movies
        """
        base_url = "https://letterboxd.com/films/language/tamil/page/"
        
        for page_num in range(start_page, end_page + 1):
            try:
                # Construct page URL
                page_url = f"{base_url}{page_num}/"
                
                # Scrape the page
                movies = self.scrape_single_page(page_url)
                
                # Push to Supabase
                self.push_to_supabase(movies)
                
                # Confirmation print
                print(f"Page {page_num} scraped and uploaded successfully")
                
                # Optional: Add a small delay between page scrapes to be respectful
                time.sleep(1)
            
            except Exception as e:
                print(f"Error processing page {page_num}: {e}")

    def __del__(self):
        """
        Ensure WebDriver is closed
        """
        try:
            self.driver.quit()
        except:
            pass

def main():
    # Supabase credentials (consider using environment variables)
    SUPABASE_URL = "https://lvgxubotwvqvnuweofor.supabase.co"
    SUPABASE_KEY = "XXXX"

    # Initialize and run scraper
    try:
        scraper = LetterboxdScraper(SUPABASE_URL, SUPABASE_KEY)
        
        # Scrape pages 1 to 72
        scraper.scrape_multiple_pages(1, 72)
    
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()