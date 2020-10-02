import json
import scrapy

from pprint import pprint
from urllib.parse import parse_qs, urlparse


class RussiaTravelLandmark(scrapy.Spider):
    name = 'russia_travel_landmark'
    start_urls = ['https://russia.travel/']

    groups_url = (
        'https://russia.travel/api/proxy/json/?url=http://api.russia.travel/api'
        '/types/frontend/v1/json/rus/group'
    )
    object_url = (
        'https://russia.travel/api/proxy/json/?url=http://api.russia.travel/api'
        '/travels/frontend/v3/json/rus/travel?id=%s'
    )
    objects_list_url = (
        'https://russia.travel/api/proxy/json/?url=http%3A%2F%2Fapi.russia.'
        'travel%2Fapi%2Ftravels%2Ffrontend%2Fv3%2Fjson%2Frus%2Ftravels%3Fgroup'
        '%3D%s%26pagesize%3D%s%26page%3D%s'
    )
    group_links = []
    page = 1
    pagesize = 100
    pages_count = None

    def get_compilation_url(self, compilation=5):
        url = (
            'https://russia.travel/api/proxy/json/?url=http%3A%2F%2Fapi.russia.'
            'travel%2Fapi%2Ftravels%2Ffrontend%2Fv3%2Fjson%2Frus%2Ftravels%3F'
            f'group%3D{compilation}%26pagesize%3D{self.pagesize}%26page%3D'
            f'{self.page}'
        )
        return url

    def find_groups(self, response):
        items = json.loads(response.body)['items']
        group_links = [
            *map(lambda x: self.get_compilation_url(compilation=x['id']), items)
        ]
        print('\n\ngroup_links:')
        pprint(group_links)
        yield from response.follow_all(group_links, callback=self.parse_groups)

    def parse(self, response):
        yield response.follow(self.groups_url, callback=self.find_groups)

    def parse_groups(self, response):
        loads = json.loads(response.body)
        group_id = parse_qs(urlparse(response.url).query)
        object_links = [
            *map(lambda x: self.object_url % x['id'], loads['items'])
        ]

        print('\n\ngroup:\n%s' % response.url)
        yield from response.follow_all(
            object_links, callback=self.parse_object
        )

        next_link = loads['_links'].get('next', None)
        if next_link is not None:
            self.page += 1
            yield response.follow(
                self.get_compilation_url(compilation=group_id),
                callback=self.parse_groups
            )

    def parse_object(self, response):
        obj = json.loads(response.body)['item']
        yield {
            'id': obj['id'],
            'title': obj['title'],
            'district': obj['district']['name'],
            'region': obj['region']['name'],
            'regions': [*map(lambda x: x['name'], obj['regions'])],
            'type': [*map(lambda x: x['name'], obj['type'])],
            'group': [*map(lambda x: x['name'], obj['group'])],
            'short_description': obj['lid'],
            'description': obj['desc'],
            'address': obj['address'],
            'phone': obj['phone'],
            'email': obj['email'],
            'geo': {
                'lon': obj['geo'].get('lon', ''),
                'lat': obj['geo'].get('lat', ''),
            },
            'tags': obj['tags'],
            'images': self.get_images(obj['images']),
        }

    def get_images(self, images):
        if len(images) == 0:
            return None

        return [*map(lambda x: self.get_image(x), images)]

    def get_image(self, image):
        return {
            'title': image['title'],
            'copyright': self.get_copyright(image['copyright']),
            'image': image['image']['src'],
            'thumb': image['thumb']['src'],
        }

    def get_copyright(self, copyright_):
        if not copyright_:
            return []

        if isinstance(copyright_, dict):
            return [copyright_.get('name')]

        return [*map(lambda x: x.get('name'), copyright_)]



