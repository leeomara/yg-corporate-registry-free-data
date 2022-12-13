import scrapy
from urllib.parse import urlencode, parse_qs, urlsplit, urlunsplit

class EntitySpider(scrapy.Spider):
    name = "entities"
    query_to = 1_000_000
    query_length_limit = 4

    def start_requests(self):
        for first_ten in range(0, 10):
            url = 'https://ycor-reey.gov.yk.ca/search?name=' + str(first_ten)
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        if not "unseen" in self.state:
            self.setup_unseen_list()

        current = self.get_query(response)

        if response.css('h5::text').get() == 'More than 100 entities found. Please be more specific.':
            self.log(f'Too many results for {response.url}')
            # return self.too_many_results(response)

            if len(current) == self.query_length_limit:
                # We've hit the limit, stop here.
                self.log(f'Hit limit with {response.url}, proceed no further')
                # Maybe move this to a downloader middleware?
                return

            # Not at the limit, so possibly create 10 new sub-requests
            for i in range(0,10):
                next_query = current + str(i)

                # Should we run this query?
                if not self.any_unseen(next_query):
                    self.log(f"No point in querying {next_query}, skipping")
                    next

                scheme, netloc, path, query_string, fragment = urlsplit(response.url)
                query_params = parse_qs(query_string)
                query_params['name'] = [next_query]
                new_query_string = urlencode(query_params, doseq=True)

                next_page = urlunsplit((scheme, netloc, path, new_query_string, fragment))
                yield scrapy.Request(next_page, callback=self.parse)
        else:

            # Delete all matching ID numbers from the "unseen" list.
            self.mark_as_seen(current)

            for entity in response.css("table tbody tr"):
                # TODO record the query number and all it's possible matches
                yield {
                    'name': entity.css('td.name-view span span::text').get(),
                    # Most don't have a former name here, but some do.
                    'former_name': entity.css('td.name-view').re_first(r'<b>Former Name:<\/b\>\xa0(.*)'),
                    'type': entity.css('span.entity-entity-type-translated::text').get(),
                    'number': entity.css('span.entity-fileno::text').get(),
                    'jurisdiction': entity.css('span.entity-jurisdiction::text').get(),
                    'status': entity.css('span.entity-status-translated::text').get(),
                    'query': current
                    # Filing and Profile reports are URLs that can be generated based on registry number.
                }

    def get_query(self, response):
        # Get current query "name" (number)
        # First to determine if we should keep going.
        scheme, netloc, path, query_string, fragment = urlsplit(response.url)
        query_params = parse_qs(query_string)

        return query_params['name'][0] # FIXME this needs be more defensive.


    def setup_unseen_list(self):
        self.state['unseen'] = [str(item).zfill(len(str(self.query_to))) for item in range(0, self.query_to)]

    def mark_as_seen(self, query):
        before_count = len(self.state['unseen'])
        self.state['unseen'] = list(filter(lambda id: query not in id, self.state['unseen']))
        after_count = len(self.state['unseen'])
        diff_count = before_count - after_count
        self.log(f"Unseen has {after_count} remaining. Marked {diff_count} as seen for '{query}'.")

    def any_unseen(self, query):
        for unseen_id in self.state['unseen']:
            if query in unseen_id:
              return True
        return False
