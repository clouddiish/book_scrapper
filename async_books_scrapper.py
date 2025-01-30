import aiohttp
import asyncio
import time
import csv
from bs4 import BeautifulSoup


class HttpError(Exception):
    def __init__(self, message, error_code):
        super().__init__(message)
        self.error_code = error_code


def get_urls():
    base_url = (
        "https://books.toscrape.com/catalogue/category/boks/nonfiction_13/page-{}.html"
    )
    return [base_url.format(page) for page in range(1, 7)]


async def fetch_book_cards_from_page(session, url):
    async with session.get(url) as response:
        if not response.ok:
            raise HttpError("Http error occured", response.status)
        page = await response.read()
        soup = BeautifulSoup(page, "html.parser")
        results = soup.find("div", class_="col-sm-8 col-md-9")
        return results.find_all("article", class_="product_pod")


async def fetch_all_book_cards(urls):
    try:
        async with aiohttp.ClientSession() as session:
            tasks = [fetch_book_cards_from_page(session, url) for url in urls]
            results = await asyncio.gather(*tasks)
            return [book_card for page_results in results for book_card in page_results]
    except HttpError as http_err:
        print("Http error: code ", http_err.error_code)
    except TypeError:
        print("Error: couldn't fetch all book cards")
    except Exception as error:
        print(f"Error: {error}")


def extract_book_data(book_card):
    title = book_card.find_all("a")[1].text.strip()
    rating = book_card.find("p", class_="star-rating")["class"][1]
    price = book_card.find("p", class_="price_color").text.strip("£")

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
    book_cards = await fetch_all_book_cards(urls)
    write_books_to_csv(book_cards, "async_books.csv")


if __name__ == "__main__":
    asyncio.run(main())
