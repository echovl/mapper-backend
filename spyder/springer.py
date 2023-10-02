import scrapy
from scrapy import responsetypes


class SpringerSpyder(scrapy.Spider):
    name = "springer"
    custom_settings = {"LOG_LEVEL": "DEBUG", "DOWNLOAD_DELAY": 0.1}

    def __init__(self, query=None, *args, **kwargs):
        super(SpringerSpyder, self).__init__(*args, **kwargs)
        self.start_urls = [
            f"https://link.springer.com/search?query={query}&facet-content-type=%22Article%22"
        ]

    def parse(self, response: responsetypes.Response):
        for book in response.css("ol#results-list li"):
            book_page = book.css("a.title::attr(href)").get()
            if book_page is not None:
                yield response.follow(book_page, callback=self.parse_book_content)

        # Follow next page
        next_page = response.css("a.next::attr(href)").get()
        if next_page is not None:
            yield response.follow(next_page, callback=self.parse)

    def parse_book_content(self, response: responsetypes.Response):
        title = response.css("h1.c-article-title::text").get()
        abstract = response.css("div#Abs1-content p::text").get()

        for item in response.css("ul[data-test*='publication-history'] li"):
            if item is None:
                continue

            doi_title = response.css(
                "p abbr[title*='Digital Object Identifier']::text"
            ).get()
            if doi_title is None:
                continue

            doi = response.css(
                "p span.c-bibliographic-information__value::text").get()

        yield {"title": title, "url": response.url, "abstract": abstract, "doi": doi}
