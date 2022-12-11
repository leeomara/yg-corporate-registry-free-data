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
