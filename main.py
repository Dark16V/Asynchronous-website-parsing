import aiohttp
import asyncio
import json
import csv
import os
from bs4 import BeautifulSoup
import time

headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
    'Accept-Language': 'en-US,en;q=0.5',
    'Accept-Encoding': 'gzip, deflate, br',
    'Connection': 'keep-alive'
}

def load_existing_data(json_file='books_data.json'):
    if os.path.exists(json_file):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            print(f"Loaded {len(data)} existing book records from {json_file}")
            return data
        except Exception as e:
            print(f"Error loading {json_file}: {e}")
            return []
    return []

async def fetch_page(session, url, retries=2, delay=1):
    for attempt in range(retries + 1):
        try:
            async with session.get(url, headers=headers, timeout=5) as response:
                response.raise_for_status()
                return await response.text()
        except (aiohttp.ClientError, asyncio.TimeoutError) as e:
            if attempt < retries:
                print(f"Error requesting {url} (attempt {attempt + 1}/{retries + 1}): {e}. Retrying in {delay} sec.")
                await asyncio.sleep(delay)
            else:
                print(f"Failed to load {url} after {retries + 1} attempts: {e}")
                return None

async def scrape_page(session, page_id, existing_links):
    url = f"https://goodreads.com/book/show/{page_id}"
    if url in existing_links:
        print(f"Skipping book with ID {page_id} (already in data)")
        return None

    html = await fetch_page(session, url)
    if not html:
        return None

    soup = BeautifulSoup(html, 'lxml')

    try:
        title = soup.find('h1', class_='Text Text__title1')
        if not title:
            print(f"Book with ID {page_id} not found")
            return None
        title = title.text

        author = soup.find('span', class_='ContributorLink__name')
        author = author.text if author else "Not specified"

        rating = soup.find('div', class_='RatingStatistics__rating')
        rating = rating.text if rating else "0"

        evaluations = soup.find('div', class_='RatingStatistics__meta')
        evaluations = evaluations.text.split('ratings')[0].strip() if evaluations else "0"

        pages = soup.find('div', class_='FeaturedDetails')
        if pages:
            pages_text = pages.text.split('published')
            published = pages_text[1].strip() if len(pages_text) > 1 else "Not specified"
            pages = pages_text[0].split(' ')[0] if pages_text[0].split(' ') else "0"
        else:
            pages = "0"
            published = "Not specified"

        description = soup.find('span', class_='Formatted')
        description = description.text if description else "No description"

        return {
            'title': title,
            'rating': rating,
            'author': author,
            'evaluations': evaluations,
            'pages': pages,
            'description': description,
            'link': url
        }
    except Exception as e:
        print(f"Error parsing page {url}: {e}")
        return None

async def scraping(limit: int, max_concurrent=10):    #<---- max_concurrent - the maximum number of asynchronous requests, can be set at your discretion.
    existing_data = load_existing_data()
    existing_links = {item['link'] for item in existing_data if 'link' in item}

    items = existing_data
    semaphore = asyncio.Semaphore(max_concurrent)

    async def limited_scrape_page(page_id):
        async with semaphore:
            return await scrape_page(session, page_id, existing_links)

    async with aiohttp.ClientSession() as session:
        tasks = [limited_scrape_page(p) for p in range(1, limit + 1)]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for result in results:
            if result and not isinstance(result, Exception):
                items.append(result)

    print(f"Collected {len(items) - len(existing_data)} new items, total {len(items)} items")
    return items

def save_json(items):
    print(f"Saving {len(items)} items to JSON")
    with open('books_data.json', 'w', encoding='utf-8') as json_file:
        json.dump(items, json_file, ensure_ascii=False, indent=2)
    print('Data saved to JSON file.')

def save_csv(items):
    print(f"Saving {len(items)} items to CSV")
    csv_headers = ['title', 'rating', 'author', 'evaluations', 'pages', 'description', 'link']
    with open('books_data.csv', 'w', encoding='utf-8', newline='') as csv_file:
        csv_writer = csv.DictWriter(csv_file, fieldnames=csv_headers)
        csv_writer.writeheader()
        csv_writer.writerows(items)
    print('Data saved to CSV file.')

if __name__ == "__main__":
    start_time = time.time()
    items = asyncio.run(scraping(10))   #<--- limit = +-100,000
    save_csv(items)
    save_json(items)
    print(f"Execution time: {time.time() - start_time:.2f} seconds")