import scrapy
from urllib.parse import urlencode, parse_qs, urlsplit, urlunsplit


class EntitySpider(scrapy.Spider):
    name = "entities"

    def start_requests(self):
        for first_ten in range(0, 10):
            url = "https://ycor-reey.gov.yk.ca/search?name=" + str(9 - first_ten)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if self.too_many_results(response):
            self.log(f"Too many results for {response.url}")
            current = self.get_query(response.url)
            # Create 10 new sub-requests
            for i in range(0, 10):
                next_query = current + str(i)
                next_page = self.url_with_query(response.url, next_query)
                yield scrapy.Request(url=next_page, callback=self.parse)
        else:
            for entity in response.css("table tbody tr"):
                yield {
                    "number": entity.css("span.entity-fileno::text").get(),
                    "name": entity.css("td.name-view span span::text").get(),
                    # Most don't have a former name here, but some do.
                    "former_name": entity.css("td.name-view").re_first(
                        r"<b>Former Name:<\/b\>\xa0(.*)"
                    ),
                    "kind": entity.css(
                        "span.entity-entity-type-translated::text"
                    ).get(),
                    "jurisdiction": entity.css("span.entity-jurisdiction::text").get(),
                    "status": entity.css("span.entity-status-translated::text").get()
                    # Filing and Profile reports are URLs that can be generated based on registry number.
                }

    def too_many_results(self, response):
        return (
            response.css("h5::text").get()
            == "More than 100 entities found. Please be more specific."
        )

    def get_query(self, url):
        # Get current query "name" (number)
        # First to determine if we should keep going.
        scheme, netloc, path, query_string, fragment = urlsplit(url)
        query_params = parse_qs(query_string)

        return query_params["name"][0]  # FIXME this needs be more defensive.

    def url_with_query(self, url, query):
        scheme, netloc, path, query_string, fragment = urlsplit(url)
        query_params = parse_qs(query_string)
        query_params["name"] = [query]
        new_query_string = urlencode(query_params, doseq=True)
        return urlunsplit((scheme, netloc, path, new_query_string, fragment))
