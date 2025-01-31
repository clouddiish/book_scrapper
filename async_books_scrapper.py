import aiohttp
import asyncio
import csv
import logging
from bs4 import BeautifulSoup

logger = logging.getLogger(__name__)
logger.setLevel("DEBUG")

console_handler = logging.StreamHandler()
console_handler.setLevel("DEBUG")

formatter = logging.Formatter(
    "{asctime} [{levelname}]: {message}", style="{", datefmt="%Y-%m-%d %H:%M"
)
console_handler.setFormatter(formatter)

logger.addHandler(console_handler)


class HttpError(Exception):
    """
    Custom exception to handle HTTP errors during web scraping.

    Args:
        message (str): The error message.
        error_code (int): The HTTP error status code.
    """

    def __init__(self, message, error_code):
        super().__init__(message)
        self.error_code = error_code


async def fetch_number_of_pages():
    """
    Fetch number of pages on the site to scrap from.

    Returns:
        int: Number of pages on the site to scrap from.
    """
    url = "https://books.toscrape.com"

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as response:
                if not response.ok:
                    raise HttpError(
                        f"Http error occured in url {url} with code {response.status}",
                        response.status,
                    )

                page = await response.read()
                soup = BeautifulSoup(page, "html.parser")

                results = soup.find("li", class_="current")
                logger.info("Found maximum number of pages")
                return int(results.text.split()[3])
    except Exception as error:
        logger.error(f"Unable to fetch number of pages, {error}")


async def get_urls():
    """
    Generate a list of URLs to scrape book data from.

    Returns:
        list: A list of formatted URLs for different pages of books.
    """
    try:
        base_url = "https://books.toscrape.com/catalogue/page-{}.html"
        number_of_pages = await fetch_number_of_pages()
        logger.info("Getting list of URLs")
        return [base_url.format(page) for page in range(1, number_of_pages + 1)]

    except Exception as error:
        logger.error(f"Unable get list of URLs, {error}")


async def fetch_book_cards_from_page(session, sem, url):
    """
    Fetch book cards from a single page and parse the HTML.

    Args:
        session (aiohttp.ClientSession): The HTTP session for making requests.
        sem (asyncio.Semaphore): Semaphore to limit concurrent requests.
        url (str): The URL of the page to scrape.

    Returns:
        list: A list of book card elements parsed from the HTML.
        If no results are found, returns an empty list.
    """
    async with sem:
        try:
            async with session.get(url) as response:

                if not response.ok:
                    raise HttpError(
                        f"Http error occured in url {url} with code {response.status}",
                        response.status,
                    )

                page = await response.read()
                soup = BeautifulSoup(page, "html.parser")

                results = soup.find("div", class_="col-sm-8 col-md-9")
                if results is None:
                    return []

                return results.find_all("article", class_="product_pod")

        except HttpError as http_err:
            logger.error(
                f"Unable to fetch book cards from page {url}. Http error occured with code {http_err.error_code}"
            )
            return []


async def fetch_all_book_cards(urls, sem):
    """
    Fetch book cards from multiple pages concurrently.

    Args:
        urls (list): A list of URLs to scrape.
        sem (asyncio.Semaphore): Semaphore to limit concurrent requests.

    Returns:
        list: A flattened list of book cards from all pages.
    """
    try:
        logger.info("Fetching books cards")
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_book_cards_from_page(session, sem, url) for url in urls]
            results = await asyncio.gather(*tasks)
            return [book_card for page_results in results for book_card in page_results]
    except Exception as error:
        logger.error(f"Unable to fetch book cards, {error}")
        return []


def extract_book_data(book_card):
    """
    Extract title, rating, and price from a single book card.

    Args:
        book_card (BeautifulSoup): A BeautifulSoup object representing a single book card.

    Returns:
        tuple: A tuple containing the book's title (str), rating (int), and price (str).
    """
    title = book_card.find_all("a")[1].text.strip()
    rating = book_card.find("p", class_="star-rating")["class"][1]
    price = book_card.find("p", class_="price_color").text.strip("£")

    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    rating = rating_map.get(rating, 0)

    return title, rating, price


def write_books_to_csv(book_cards, filename):
    """
    Write the extracted book data to a CSV file.

    Args:
        book_cards (list): A list of book cards to process.
        filename (str): The name of the CSV file to write the data to.

    Raises:
        TypeError: If there's an issue writing the data to the CSV file.
    """
    logger.info(f"Writing {len(book_cards)} book records to file {filename}")

    try:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["title", "rating", "price"])

            for book_card in book_cards:
                writer.writerow(extract_book_data(book_card))

        logger.info(
            f"Successfuly wrote {len(book_cards)} book records to file {filename}"
        )

    except Exception as error:
        logger.error(f"Unable to write to csv file, {error}")


async def main():
    """
    Main function to coordinate the scraping and writing of book data.

    1. Generates URLs.
    2. Fetches book data from multiple pages concurrently.
    3. Writes the book data to a CSV file.
    """
    logger.info("Web scrapper started")
    urls = await get_urls()
    sem = asyncio.Semaphore(10)
    book_cards = await fetch_all_book_cards(urls, sem)
    write_books_to_csv(book_cards, "async_books.csv")
    logger.info("Web scraper ended.")


if __name__ == "__main__":
    asyncio.run(main())
