# scraper.py
import json
import requests
from bs4 import BeautifulSoup
import time

def scrape_capillary_docs():
    base_url = "https://docs.capillarytech.com/"
    urls_to_scrape = [
        "https://docs.capillarytech.com/reference/authentication",
        "https://docs.capillarytech.com/reference/customers",
        "https://docs.capillarytech.com/reference/loyalty-campaigns",
        "https://docs.capillarytech.com/reference/transactions",
        "https://docs.capillarytech.com/guides/getting-started"
    ]

    scraped_data = []

    for url in urls_to_scrape:
        print(f"Scraping: {url}")
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            soup = BeautifulSoup(response.text, 'html.parser')

            # Try to get main content — adjust selector if needed
            content_div = soup.find('main') or soup.find('article') or soup.find('div', class_='content')
            if not content_div:
                content_div = soup  # fallback: take entire body

            text_content = content_div.get_text(separator="\n", strip=True)

            scraped_data.append({
                "url": url,
                "content": text_content[:10000]  # Limit to avoid overload
            })

            time.sleep(1)  # Be respectful

        except Exception as e:
            print(f"⚠️ Failed to scrape {url}: {e}")
            scraped_data.append({
                "url": url,
                "content": f"ERROR: Could not scrape this page. Reason: {str(e)}"
            })

    # Save with UTF-8 encoding
    with open("data/docs.json", "w", encoding="utf-8") as f:
        json.dump(scraped_data, f, indent=2, ensure_ascii=False)

    print(f"✅ Scraped {len(scraped_data)} pages. Saved to data/docs.json")

if __name__ == "__main__":
    scrape_capillary_docs()