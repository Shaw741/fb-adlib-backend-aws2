# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
import json
from itemadapter import ItemAdapter


class FbAdlibPipeline:

    def open_spider(self, spider):
        self.file = open('items.jl', 'w')
        self.file.write("[" + "\n")

    def close_spider(self, spider):
        self.file.write("\n" + "]")
        self.file.close()

    def process_item(self, item, spider):
        line = json.dumps(ItemAdapter(item).asdict()) + ","
        self.file.write(line)
        return item