# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FbAdlibItem(scrapy.Item):
    # define the fields for your item here like:
    status = scrapy.Field()
    startDate = scrapy.Field()
    platforms = scrapy.Field()
    adID = scrapy.Field()
    noOfAds = scrapy.Field()
    displayURL = scrapy.Field()
    headline = scrapy.Field()
    ctaStatus = scrapy.Field()
    leadingURL = scrapy.Field()
