# Movies Scraper

## Overview  
Python automation task is designed to efficiently scrape Tamil movie metadata from Letterboxd, used **Selenium** for web scraping, **BeautifulSoup** for parsing HTML, and **Supabase** as the database. Automation was implemented to handle data extraction across multiple pages, ensuring that all relevant details were collected and stored seamlessly. Research into the structure of the website and the volume of data helped refine the scraping strategy. When technical challenges hit, AI is used for guidance and troubleshooting, streamlining the overall implementation.

## Initialization  
- A **Supabase** SaaS database was set up to store the scraped movie metadata.  
- Research indicated that Letterboxd hosts around 5,000 Tamil movies, with each page displaying up to 72 movies.(https://letterboxd.com/films/language/tamil/page/1/)  
- The scraper was designed to target specific `<li>` tags containing the required metadata, ensuring accuracy and completeness.  
- ChatGPT is used to resolve challenges, aiding in the design of an efficient and robust scraping process.  

## Scraping Process  
- Each page was dynamically loaded using Selenium, ensuring all elements were fully rendered before parsing the HTML with BeautifulSoup.  
- Relevant metadata such as `film-id`, `film-name`, `film-slug`, and `release-year` was extracted from `<li>` tags, ensuring only essential information was processed.  
- Data was uploaded to Supabase using its REST API and a secure API key, with confirmation logged after each successful page upload.  
- For error handling, the scraper implemented a retry mechanism, attempting up to three times in case of connection or network failures. This ensured reliability and minimized data loss during execution.
