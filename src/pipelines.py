from itemadapter import ItemAdapter
from slugify import slugify

from scrapy import signals
from scrapy.exceptions import DropItem
from scrapy.exporters import CsvItemExporter


class SrcPipeline:
    def process_item(self, item, spider):
        return item


class MultipleCsvPipeline:
    def __init__(self):
        self.csvfiles = {}
        self.exporter = {}

    @classmethod
    def from_crawler(cls, crawler):
        pipeline = cls()
        crawler.signals.connect(pipeline.close_spider, signals.spider_closed)
        return pipeline

    def close_spider(self, spider):
        for e in self.exporter.values():
            e.finish_exporting()
        for f in self.csvfiles.values():
            f.close()

    def process_item(self, item, spider):
        region = item.get('Регион:')
        if not region:
            region = 'other'
        csv = slugify(region) + '.csv'
        if csv not in self.csvfiles:
            newfile = open(
                'parsed/tourism_classification_hotels/part2/' + csv, 'wb'
            )
            self.csvfiles[csv] = newfile
            self.exporter[csv] = CsvItemExporter(newfile)
            self.exporter[csv].start_exporting()
        self.exporter[csv].export_item(item)

        return item


class DuplicatesPipeline:
    def __init__(self):
        self.ids_seen = set()

    def process_item(self, item, spider):
        adapter = ItemAdapter(item)
        if adapter['id'] in self.ids_seen:
            raise DropItem("Duplicate item found: %r" % item)
        else:
            self.ids_seen.add(adapter['id'])
            return item
