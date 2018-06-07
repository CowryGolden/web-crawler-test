# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class BudejieItem(scrapy.Item):
    username = scrapy.Field()
    content = scrapy.Field()

# 注意这两个属性类型都必须是列表，（www.meizitu.com 专用）
class MeizituImageItem(scrapy.Item):
    image_urls = scrapy.Field()
    images = scrapy.Field()

# www.mm131.com 专用    
class Mm131ImageItem(scrapy.Item):
    image_urls = scrapy.Field()
    images = scrapy.Field()
    referer = scrapy.Field()    # referer字段，用于保存该图片的Referer。

# csdn blog 备份专用
class CsdnBlogItem(scrapy.Item):
    title = scrapy.Field()
    content = scrapy.Field()    