# asynchronous book scrapper

Asynchronous book scrapper is a web scrapper for extracting book data from the website [Books to Scrape](https://books.toscrape.com/). It uses Python's `aiohttp` library for concurrent HTTP requests and `BeautifulSoup` for HTML parsing. The scraper collects book titles, ratings, and prices and writes the extracted data to a CSV file.

## features

- **asynchronous requests** - fetches multiple pages concurrently, improving performance
- **HTML parsing** - extracts book details (title, rating, price) using `BeautifulSoup`
- **CSV output** - saves the scraped book data to a CSV file
- **custom error handling** - handles HTTP errors with a custom HttpError exception
- **logging** - provides detailed logs for debugging and tracking progress

## getting started

### dependencies

- Python 3.8 or later
- Python packages:
  - `aiohttp`
  - `beautifulsoup4`
```
pip install aiohttp beautifulsoup4
```

### installation

- clone the repository or copy the script
```
git clone https://github.com/clouddiish/book_scrapper.git
```

### run

- run the script with the below command. Note: if needed replace the `async_books_scrapper.py` with the name of the script
```
python async_books_scrapper.py
```

### output

- once the script completes, the scraped data will be available in `async_books.csv`

## notes

- the script was developed for educational purposes only; ensure compliance with the website's terms of service before scraping
- if the website structure changes, the scrapping logic may need updates
