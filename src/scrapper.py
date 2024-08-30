import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime
from utils import (
    fetch_article_links, 
    filter_and_scrape_articles, 
    read_config, 
    save_articles_per_date,  
   save_articles_per_article
)

def run_scraper():
    # Start measuring time
    start_time = time.time()
    
    # Load URLs from a CSV file
    csv_filename = '../Source/source.csv'  # Adjust path if needed
    sites = read_config(csv_filename)
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
    }
    
    all_article_links = []
    target_date = datetime.strptime("29-08-2024", "%d-%m-%Y").date()

    # Use ThreadPoolExecutor to fetch articles concurrently
    with ThreadPoolExecutor(max_workers=5) as executor:
        future_to_site = {}
        for site in sites:
            future = executor.submit(
                fetch_article_links, 
                site['page_url'], 
                headers,  
                target_date,
                site['navigation_type'],
                site['time_tag'], 
                site['time_class']
            )
            future_to_site[future] = site

        for future in as_completed(future_to_site):
            site = future_to_site[future]
            try:
                article_links = future.result()
                all_article_links.extend(article_links)
                time.sleep(5)  # Delay between requests to avoid overloading the server
            except Exception as e:
                print(f"Error processing site {site['page_url']}: {e}")
    
    print("Filtering articles and scraping content...")
 # Format date for filename
    
    # Filter and scrape articles based on the target date
    results = filter_and_scrape_articles(all_article_links, target_date)
    
    # Save all articles per date to a CSV file
    save_articles_per_date(results,target_date)
    
    # Save each article to an individual Excel file
    for article in results:
       save_articles_per_article(article)
    
    print("Articles have been saved.")
    
    # Stop measuring time and print the elapsed time
    end_time = time.time()
    elapsed_time = end_time - start_time
    print(f"Execution time: {elapsed_time:.2f} seconds")
