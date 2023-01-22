# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from scrapy.exceptions import IgnoreRequest

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter


class YcorScraperSpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class YcorScraperDownloaderMiddleware:

    def __init__(self, query_to=1_000_000):
        self.query_length_limit = len(str(query_to))
        self.unseen = [str(item).zfill(self.query_length_limit - 1) for item in range(0, query_to)]

    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        return cls(
            query_to=crawler.settings.get('QUERY_TO')
        )

    def process_request(self, request, spider):
        # Should we run this query?

        # Don't apply to the robots.txt query.
        if self.is_robots_url(request.url):
          return None

        query = spider.get_query(request.url)

        if len(query) >= self.query_length_limit:
            # We've hit the limit.
            spider.logger.info(f'Hit limit with {request.url}, ignore request.')
            raise IgnoreRequest

        if not self.any_unseen(query):
            spider.logger.info(f"No point in querying {query}, ignore request.")
            raise IgnoreRequest

        # - return None: continue processing this request
        return None

    def process_response(self, request, response, spider):
        # Unless there are too many results (in which case no records are returned),
        # delete all matching ID numbers from the "unseen" list.

        # Don't apply to the robots.txt query.
        if self.is_robots_url(response.url):
          return response

        if not spider.too_many_results(response):
            query = spider.get_query(response.url)
            before_count = len(self.unseen)
            self.unseen = list(filter(lambda id: query not in id, self.unseen))
            after_count = len(self.unseen)
            diff_count = before_count - after_count
            spider.logger.info(f"Unseen has {after_count} remaining. Marked {diff_count} as seen for '{query}'.")

        return response

    def any_unseen(self, query):
        for unseen_id in self.unseen:
            if query in unseen_id:
              return True
        return False

    def is_robots_url(self, url):
        return "robots.txt" in url
