import scrapy

from urllib.parse import parse_qs, urlparse, unquote


class TourismClassificationHotelSpider(scrapy.Spider):
    name = 'tourism_classification_hotel'

    def __init__(self, urls):
        self.start_urls = urls

    def parse(self, response):
        hotel_links_xpath = (
            "//div[@id='yw1']/div[@class='items']/div[@class='object']/"
            "div[@class='object-left']/a/@href"
        )
        print('\nПарсинг отелей страницы [%s]' % response.url)
        yield from response.follow_all(
            response.xpath(hotel_links_xpath), callback=self.hotel_page_parse
        )

        current_page = self.get_current_page(response.url)
        links = {
            int(link_el.xpath('text()').get(default=0)): link_el.xpath('@href').get(default='') # NOQA
            for link_el in response.xpath(
                "//div[@id='yw1']/div[@class='pager']/"
                "ul[@class='pagination']/li[@class='page']/a"
            )
        }
        nearest_links = [
            t[1] for t in filter(
                lambda t, current_page=current_page: t[0] > current_page,
                links.items()
            )
        ]
        if nearest_links:
            yield response.follow(nearest_links[0], callback=self.parse)

    def hotel_page_parse(self, response):
        detail_fields = response.xpath(
            "//div[@class='content']/div[@class='content_left']/"
            "div[@class='detail-fields']/div[@class='detail-field']"
        )
        obj = {
            'url': response.url,
        }
        for detail_field in detail_fields:
            label = detail_field.css('.detail-label::text').get()
            value = detail_field.css('.detail-value::text').get()
            obj[label] = value

        if len(obj.keys()) > 1:
            obj['status'] = 'Parsed'
        else:
            obj['status'] = 'Error'

        yield obj

    def get_current_page(self, url):
        return int(parse_qs(urlparse(url).query)['Accommodation_page'][0])
