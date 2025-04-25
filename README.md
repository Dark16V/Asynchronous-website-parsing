# Asynchronous-website-parsing
This is a Python script that asynchronously scrapes book data from Goodreads using asyncio and aiohttp. The script collects book details such as title, author, rating, number of evaluations, page count, description, and URL, and saves them to JSON and CSV files. It checks for existing book IDs in the output file to avoid duplicate scraping and limits concurrent requests to prevent server overload.

Features

* Asynchronous scraping: Uses asyncio and aiohttp for fast and efficient HTTP requests.

* Duplicate checking: Skips books already present in the output JSON file based on their URL.

* Concurrent request limiting: Uses asyncio.Semaphore to restrict simultaneous requests (default: 5).

* Error handling: Retries failed requests and handles exceptions gracefully.

* Output formats: Saves data to both books_data.json and books_data.csv.

Prerequisites

* Python: Version 3.7 or higher.

* Virtual Environment (recommended): To manage dependencies.

Installation

1. Clone the repository:

        git clone https://github.com/your-username/goodreads-scraper.git
        cd goodreads-scraper

2. Set up a virtual environment:

        python -m venv venv

   And activate:

        source venv/bin/activate  # Linux/Mac
        venv\Scripts\activate     # Windows

3. Install dependencies:

        pip install -r requirements.txt

Usage

1. Run the script:

        python scraper.py

  * By default, the script scrapes data for books with IDs 1 to 10 (configurable).

2. Output files:

* books_data.json: Contains scraped book data in JSON format.

* books_data.csv: Contains the same data in CSV format.

3. Customize scraping:

* Modify the limit parameter in scraper.py to scrape a different number of books:

      items = asyncio.run(scraping(10))  # Change 10 to desired number

* Adjust the max_concurrent parameter to control simultaneous requests (default: 10):

      items = asyncio.run(scraping(10, max_concurrent=5))  # Increase for faster scraping
