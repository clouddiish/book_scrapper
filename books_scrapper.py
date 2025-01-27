import requests
import csv
from bs4 import BeautifulSoup


def get_urls():
    base_url = (
        "https://books.toscrape.com/catalogue/category/books/nonfiction_13/page-{}.html"
    )
    return [base_url.format(page) for page in range(1, 7)]


def fetch_book_cards_from_page(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find("div", class_="col-sm-8 col-md-9")
    return results.find_all("article", class_="product_pod")


def fetch_all_book_cards(urls):
    book_cards_list = []
    for url in urls:
        book_cards_list += fetch_book_cards_from_page(url)
    return book_cards_list


def extract_book_data(book_card):
    title = book_card.find_all("a")[1].text.strip()
    rating = book_card.find("p", class_="star-rating")["class"][1]
    price = book_card.find("p", class_="price_color").text.strip("£")

    return title, rating, price


def write_books_to_csv(book_cards, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "rating", "price"])

        for book_card in book_cards:
            writer.writerow(extract_book_data(book_card))


def main():
    urls = get_urls()
    book_cards = fetch_all_book_cards(urls)
    write_books_to_csv(book_cards, "books.csv")


if __name__ == "__main__":
    main()
