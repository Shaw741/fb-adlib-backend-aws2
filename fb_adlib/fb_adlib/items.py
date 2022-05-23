# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FbAdlibItem(scrapy.Item):
    status = scrapy.Field()
    startDate = scrapy.Field()
    platforms = scrapy.Field()
    adID = scrapy.Field()
    noOfCopyAds = scrapy.Field()


    adMediaURL = scrapy.Field()
    adMediaType = scrapy.Field()
    bucketMediaURL = scrapy.Field()
    adDescription = scrapy.Field()

    displayURL = scrapy.Field()
    headline = scrapy.Field()
    ctaStatus = scrapy.Field()
    purchaseURL = scrapy.Field()
    purchaseDescription = scrapy.Field()

    pageInfo = scrapy.Field()


class PageInfo(scrapy.Item):
    name = scrapy.Field() 
    url = scrapy.Field() 
    logo = scrapy.Field() 
    # platform = scrapy.Field() 
    description = scrapy.Field() 

# class PagePlatformInfo(scrapy.Item):
#     name = scrapy.Field() 
#     id = scrapy.Field() 
#     likes = scrapy.Field() 
#     followers = scrapy.Field() 
#     type = scrapy.Field() 
