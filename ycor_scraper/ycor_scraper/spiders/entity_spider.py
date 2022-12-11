import scrapy


class Entitypider(scrapy.Spider):
    name = "entities"

    def start_requests(self):
        urls = [
            'https://ycor-reey.gov.yk.ca/search?name=0001',
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        page = '0001'
        filename = f'entities-{page}.html'
        with open(filename, 'wb') as f:
            f.write(response.body)
        self.log(f'Saved file {filename}')
        for entity in response.css("table tbody tr"):
            yield {
                'name': entity.css('td.name-view span span::text').get(),
                # Most don't have a former name here, but some do.
                'former_name': entity.css('td.name-view').re_first(r'<b>Former Name:<\/b\>\xa0(.*)'),
                'entity_type': entity.css('span.entity-entity-type-translated::text').get(),
                'registry_number': entity.css('span.entity-fileno::text').get(),
                'jurisdiction': entity.css('span.entity-jurisdiction::text').get(),
                'status': entity.css('span.entity-status-translated::text').get()
                # Filing and Profile reports are URLs that can be generated based on registry number.
            }
