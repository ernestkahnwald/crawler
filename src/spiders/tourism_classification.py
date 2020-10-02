import scrapy

from urllib.parse import parse_qs, urlparse


class TourismClassificationHotelSpider(scrapy.Spider):
    name = 'tourism_classification_hotel'

    def start_requests(self):
        urls = [
            # All
            # 'https://xn----7sba3acabbldhv3chawrl5bzn.xn--p1ai/displayAccommodation/index?Accommodation_page=1'
            # Moscow region
            # 'https://xn----7sba3acabbldhv3chawrl5bzn.xn--p1ai/displayAccommodation/index?Accommodation%5BFullName%5D=&Accommodation%5BRegion%5D=%D0%9C%D0%BE%D1%81%D0%BA%D0%BE%D0%B2%D1%81%D0%BA%D0%B0%D1%8F+%D0%BE%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C&Accommodation%5BKey%5D=&Accommodation%5BOrganizationId%5D=&Accommodation%5BCertificateNumber%5D=&Accommodation%5BInn%5D=&Accommodation%5BOgrn%5D=&Accommodation%5BSolutionNumber%5D=&yt0=%D0%9D%D0%B0%D0%B9%D1%82%D0%B8&Accommodation_page=1'
            # калина 20+
            # 'https://xn----7sba3acabbldhv3chawrl5bzn.xn--p1ai/displayAccommodation/index?Accommodation%5BFullName%5D=&Accommodation%5BRegion%5D=%D0%9A%D0%B0%D0%BB%D0%B8%D0%BD%D0%B8%D0%BD%D0%B3%D1%80%D0%B0%D0%B4%D1%81%D0%BA%D0%B0%D1%8F+%D0%BE%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C&Accommodation%5BKey%5D=&Accommodation%5BOrganizationId%5D=&Accommodation%5BCertificateNumber%5D=&Accommodation%5BInn%5D=&Accommodation%5BOgrn%5D=&Accommodation%5BSolutionNumber%5D=&yt0=%D0%9D%D0%B0%D0%B9%D1%82%D0%B8&Accommodation_page=1'
            # лен область 20+
            # 'https://xn----7sba3acabbldhv3chawrl5bzn.xn--p1ai/displayAccommodation/index?Accommodation%5BFullName%5D=&Accommodation%5BRegion%5D=%D0%9B%D0%B5%D0%BD%D0%B8%D0%BD%D0%B3%D1%80%D0%B0%D0%B4%D1%81%D0%BA%D0%B0%D1%8F+%D0%BE%D0%B1%D0%BB%D0%B0%D1%81%D1%82%D1%8C&Accommodation%5BKey%5D=&Accommodation%5BOrganizationId%5D=&Accommodation%5BCertificateNumber%5D=&Accommodation%5BInn%5D=&Accommodation%5BOgrn%5D=&Accommodation%5BSolutionNumber%5D=&yt0=%D0%9D%D0%B0%D0%B9%D1%82%D0%B8&Accommodation_page=1'
            # крым 60+
            # 'https://xn----7sba3acabbldhv3chawrl5bzn.xn--p1ai/displayAccommodation/index?Accommodation%5BFullName%5D=&Accommodation%5BRegion%5D=%D0%A0%D0%B5%D1%81%D0%BF%D1%83%D0%B1%D0%BB%D0%B8%D0%BA%D0%B0+%D0%9A%D1%80%D1%8B%D0%BC&Accommodation%5BKey%5D=&Accommodation%5BOrganizationId%5D=&Accommodation%5BCertificateNumber%5D=&Accommodation%5BInn%5D=&Accommodation%5BOgrn%5D=&Accommodation%5BSolutionNumber%5D=&yt0=%D0%9D%D0%B0%D0%B9%D1%82%D0%B8&Accommodation_page=1'
            # краснодарский край 400+
            'https://xn----7sba3acabbldhv3chawrl5bzn.xn--p1ai/displayAccommodation/index?Accommodation%5BFullName%5D=&Accommodation%5BRegion%5D=%D0%9A%D1%80%D0%B0%D1%81%D0%BD%D0%BE%D0%B4%D0%B0%D1%80%D1%81%D0%BA%D0%B8%D0%B9+%D0%BA%D1%80%D0%B0%D0%B9&Accommodation%5BKey%5D=&Accommodation%5BOrganizationId%5D=&Accommodation%5BCertificateNumber%5D=&Accommodation%5BInn%5D=&Accommodation%5BOgrn%5D=&Accommodation%5BSolutionNumber%5D=&yt0=%D0%9D%D0%B0%D0%B9%D1%82%D0%B8&Accommodation_page=1'
        ]
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

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
