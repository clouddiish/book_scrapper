import aiohttp
import asyncio
import time


def get_urls():
    base_url = (
        "https://books.toscrape.com/catalogue/category/books/nonfiction_13/page-{}.html"
    )
    return [base_url.format(page) for page in range(1, 7)]


async def fetch_page(session, url):
    async with session.get(url) as response:
        return await response.text()


async def main():
    async with aiohttp.ClientSession() as session:
        tasks = []

        for url in get_urls():
            tasks.append(fetch_page(session, url))

        htmls = await asyncio.gather(*tasks)


if __name__ == "__main__":
    asyncio.run(main())
