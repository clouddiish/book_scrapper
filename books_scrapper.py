import requests
from bs4 import BeautifulSoup

URL = "https://books.toscrape.com/catalogue/category/books/nonfiction_13/index.html"
page = requests.get(URL)

soup = BeautifulSoup(page.content, "html.parser")

results = soup.find("div", class_="col-sm-8 col-md-9")
book_cards = results.find_all("article", class_="product_pod")

for book_card in book_cards:
    title_element = book_card.find_all("a")[1]
    rating_element = book_card.find("p", class_="star-rating")
    price_element = book_card.find("p", class_="price_color")

    title = title_element.text.strip()
    rating = rating_element["class"][1]
    price = price_element.text.strip()

    print(title)
    print(rating)
    print(price)
