import aiohttp
import asyncio
import csv
from bs4 import BeautifulSoup


class HttpError(Exception):
    def __init__(self, message, error_code):
        super().__init__(message)
        self.error_code = error_code


def get_urls():
    base_url = (
        "https://books.toscrape.com/catalogue/category/books/nonfiction_13/page-{}.html"
    )
    return [base_url.format(page) for page in range(1, 8)]


async def fetch_book_cards_from_page(session, sem, url):
    async with sem:
        try:
            async with session.get(url) as response:

                if not response.ok:
                    raise HttpError(
                        f"Http error occured in url {url} with code", response.status
                    )

                page = await response.read()
                soup = BeautifulSoup(page, "html.parser")

                results = soup.find("div", class_="col-sm-8 col-md-9")
                if results is None:
                    return []

                return results.find_all("article", class_="product_pod")

        except HttpError as http_err:
            print(f"Http error occured in url {url} with code", http_err.error_code)
            return []


async def fetch_all_book_cards(urls, sem):
    async with aiohttp.ClientSession() as session:
        tasks = [fetch_book_cards_from_page(session, sem, url) for url in urls]
        results = await asyncio.gather(*tasks)
        return [book_card for page_results in results for book_card in page_results]


def extract_book_data(book_card):
    title = book_card.find_all("a")[1].text.strip()
    rating = book_card.find("p", class_="star-rating")["class"][1]
    price = book_card.find("p", class_="price_color").text.strip("£")

    rating_map = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}
    rating = rating_map.get(rating, 0)

    return title, rating, price


def write_books_to_csv(book_cards, filename):
    try:
        with open(filename, "w", newline="", encoding="utf-8") as file:
            writer = csv.writer(file)
            writer.writerow(["title", "rating", "price"])

            for book_card in book_cards:
                writer.writerow(extract_book_data(book_card))

    except TypeError:
        print("Error: couldn't write book data to csv file")

    except Exception as error:
        print(f"Error: {error}")


async def main():
    urls = get_urls()
    sem = asyncio.Semaphore(3)
    book_cards = await fetch_all_book_cards(urls, sem)
    write_books_to_csv(book_cards, "async_books.csv")


if __name__ == "__main__":
    asyncio.run(main())
