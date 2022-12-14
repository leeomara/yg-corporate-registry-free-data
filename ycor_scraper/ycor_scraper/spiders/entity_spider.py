import scrapy
from urllib.parse import urlencode, parse_qs, urlsplit, urlunsplit

class EntitySpider(scrapy.Spider):
    name = "entities"

    def start_requests(self):
        for first_ten in range(0, 10):
            url = 'https://ycor-reey.gov.yk.ca/search?name=' + str(first_ten)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        current = self.get_query(response.url)

        if response.css('h5::text').get() == 'More than 100 entities found. Please be more specific.':
            self.log(f'Too many results for {response.url}')
            # return self.too_many_results(response)

            # Create 10 new sub-requests
            for i in range(0,10):
                next_query = current + str(i)

                scheme, netloc, path, query_string, fragment = urlsplit(response.url)
                query_params = parse_qs(query_string)
                query_params['name'] = [next_query]
                new_query_string = urlencode(query_params, doseq=True)

                next_page = urlunsplit((scheme, netloc, path, new_query_string, fragment))
                yield scrapy.Request(next_page, callback=self.parse)
        else:
            for entity in response.css("table tbody tr"):
                # TODO record the query number and all it's possible matches
                yield {
                    'name': entity.css('td.name-view span span::text').get(),
                    # Most don't have a former name here, but some do.
                    'former_name': entity.css('td.name-view').re_first(r'<b>Former Name:<\/b\>\xa0(.*)'),
                    'type': entity.css('span.entity-entity-type-translated::text').get(),
                    'number': entity.css('span.entity-fileno::text').get(),
                    'jurisdiction': entity.css('span.entity-jurisdiction::text').get(),
                    'status': entity.css('span.entity-status-translated::text').get()
                    # Filing and Profile reports are URLs that can be generated based on registry number.
                }

    def get_query(self, url):
        # Get current query "name" (number)
        # First to determine if we should keep going.
        scheme, netloc, path, query_string, fragment = urlsplit(url)
        query_params = parse_qs(query_string)

        return query_params['name'][0] # FIXME this needs be more defensive.
