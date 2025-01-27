import requests
import csv
from bs4 import BeautifulSoup


def get_urls():
    urls = []
    for page in range(1, 7):
        urls.append(
            f"https://books.toscrape.com/catalogue/category/books/nonfiction_13/page-{page}.html"
        )

    return urls


def get_book_cards_from_one_page(url):
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find("div", class_="col-sm-8 col-md-9")
    book_cards = results.find_all("article", class_="product_pod")
    return book_cards


def get_book_cards_from_all_pages(urls):
    book_cards_list = []
    for url in urls:
        book_cards_list += get_book_cards_from_one_page(url)
    return book_cards_list


def write_books_data(book_cards_list, filename):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["title", "rating", "price"])

        for book_card in book_cards_list:
            title_element = book_card.find_all("a")[1]
            rating_element = book_card.find("p", class_="star-rating")
            price_element = book_card.find("p", class_="price_color")

            title = title_element.text.strip()
            rating = rating_element["class"][1]
            price = price_element.text.strip().strip("£")

            writer.writerow([title, rating, price])


def main():
    write_books_data(get_book_cards_from_all_pages(get_urls()), "books.csv")


if __name__ == "__main__":
    main()
