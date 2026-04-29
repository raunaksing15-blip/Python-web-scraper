import requests
import pandas as pd
from bs4 import BeautifulSoup
import sys
from datetime import datetime

def get_headers():
    """Returns basic headers to mimic a browser request."""
    return {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
    }

def fetch_html(url):
    """Fetches the HTML content of a given URL."""
    try:
        response = requests.get(url, headers=get_headers(), timeout=10)
        response.raise_for_status()  # Check for HTTP errors
        return response.text
    except requests.exceptions.RequestException as e:
        print(f"Error: Could not fetch the URL. {e}")
        return None

def parse_data(html, selectors):
    """
    Parses HTML and extracts data based on provided CSS selectors.
    Modify 'container' to the wrapper element of each item (e.g., a product card).
    """
    soup = BeautifulSoup(html, 'html.parser')
    results = []
    
    # Identify the container for each record (e.g., 'div.product-item')
    # For general purposes, we'll try to find common patterns or the whole page
    items = soup.select(selectors.get('container', 'body'))

    for item in items:
        # Extract data safely with defaults
        title = item.select_one(selectors.get('title'))
        price = item.select_one(selectors.get('price'))
        extra = item.select_one(selectors.get('extra'))

        data = {
            "Title": title.get_text(strip=True) if title else "N/A",
            "Price": price.get_text(strip=True) if price else "N/A",
            "Info": extra.get_text(strip=True) if extra else "N/A",
            "Scraped At": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Only add if we actually found a title
        if data["Title"] != "N/A":
            results.append(data)
            
    return results

def save_to_csv(data, filename):
    """Converts list of dicts to DataFrame and saves to CSV."""
    if not data:
        print("No data found to save.")
        return False
    
    df = pd.DataFrame(data)
    df.to_csv(filename, index=False)
    return True

def main():
    print("--- Web Scraper CLI Tool ---")
    
    # 1. User Inputs
    url = input("Enter the Website URL: ").strip()
    if not url.startswith("http"):
        print("Invalid URL. Please include http:// or https://")
        return

    filename = input("Enter output filename (default: output.csv): ").strip() or "output.csv"
    if not filename.endswith(".csv"):
        filename += ".csv"

    # 2. Configuration (User can modify these selectors based on the site)
    # Example: To scrape a bookstore, use 'h3 a' for title and '.price_color' for price
    print("\n[Optional] Define CSS Selectors (Press Enter to use defaults)")
    container_sel = input("Container Selector (e.g., .product_pod): ") or "body"
    title_sel = input("Title Selector (e.g., h3): ") or "h1"
    price_sel = input("Price Selector (e.g., .price): ") or ".price"
    
    selectors = {
        "container": container_sel,
        "title": title_sel,
        "price": price_sel,
        "extra": ".rating" # Placeholder for additional info
    }

    # 3. Execution
    print(f"\nScraping {url}...")
    html = fetch_html(url)
    
    if html:
        scraped_data = parse_data(html, selectors)
        
        if save_to_csv(scraped_data, filename):
            print("-" * 30)
            print("Scraping completed successfully!")
            print(f"Total records scraped: {len(scraped_data)}")
            print(f"Data saved to: {filename}")
            print("-" * 30)

if __name__ == "__main__":
    main()
  
