# scraper.py
import os
import json
import time
import requests
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
from typing import List, Dict

# Base URL
BASE_URL = "https://docs.capillarytech.com/"
OUTPUT_FILE = "data/docs.json"

# Create data dir
os.makedirs("data", exist_ok=True)

def get_soup(url: str):
    """Fetch page and return BeautifulSoup object"""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')
    except Exception as e:
        print(f"❌ Failed to fetch {url}: {e}")
        return None

def extract_page_content(soup: BeautifulSoup, url: str) -> str:
    """Extract main content from doc page"""
    # Main content container (based on inspection of CapillaryTech docs structure)
    content_div = soup.find('div', class_='main-content') or \
                  soup.find('article') or \
                  soup.find('div', role='main') or \
                  soup.find('main')

    if not content_div:
        # Fallback: get all paragraphs and headings
        content_div = soup

    # Extract text from common content tags
    elements = content_div.find_all(['p', 'h1', 'h2', 'h3', 'h4', 'li', 'pre', 'code', 'table'])
    texts = []
    for el in elements:
        text = el.get_text().strip()
        if text and len(text) > 15:  # Avoid tiny fragments
            texts.append(text)

    content = "\n\n".join(texts)
    return content.strip()

def find_doc_links(soup: BeautifulSoup, base_url: str) -> List[str]:
    """Find internal documentation links"""
    links = set()
    for a_tag in soup.find_all('a', href=True):
        href = a_tag['href']
        full_url = urljoin(base_url, href)
        # Only keep URLs under docs.capillarytech.com and avoid anchors / external
        if (urlparse(full_url).netloc == 'docs.capillarytech.com' and
            '#' not in href and
            not href.endswith(('.pdf', '.zip'))):
            links.add(full_url)
    return list(links)

def scrape_capillary_docs():
    """Main scraping function"""
    print("🌐 Starting scrape of CapillaryTech Docs...")

    # Start with homepage
    visited = set()
    to_visit = [BASE_URL]
    documents = []

    # Limit to first 7000 pages for demo (avoid overload)
    MAX_PAGES = 7000
    count = 0

    while to_visit and count < MAX_PAGES:
        url = to_visit.pop(0)
        if url in visited:
            continue

        print(f"📄 Fetching ({count+1}/{MAX_PAGES}): {url}")
        soup = get_soup(url)
        if not soup:
            continue

        # Extract content
        content = extract_page_content(soup, url)
        if len(content) < 0:# Skip near-empty pages
            print(f"⚠️ Skipping (too short): {url}")
            visited.add(url)
            continue

        documents.append({
            "url": url,
            "content": content
        })

        # Find new links (optional: expand crawl)
        if count < 5:  # Only explore links from first 5 pages
            new_links = find_doc_links(soup, BASE_URL)
            for link in new_links:
                if link not in visited and link not in to_visit:
                    to_visit.append(link)

        visited.add(url)
        count += 1
        time.sleep(1.5)  # Be respectful

    # Save to JSON
    with open("data/docs.json", "w", encoding="utf-8") as f:
        json.dump(documents, f, indent=2, ensure_ascii=False)

    print(f"\n✅ Scraped {len(documents)} pages.")
    print(f"💾 Saved to {OUTPUT_FILE}")
    print("\nSample URLs scraped:")
    for doc in documents[:3]:
        print(f" - {doc['url']}")

if __name__ == "__main__":
    scrape_capillary_docs()