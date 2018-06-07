#!/usr/bin/env python3
# -*- coding: utf-8 -*-

r'''
    从dmoz.org上爬取内容
'''
# 导入资源
import scrapy
from tutorial.items import DmozItem

class DmozSprider(scrapy.Spider):
    name = "dmoz"
    allowed_domains = ["dmoz.org"]
    start_urls = [
        "http://www.dmoz.org/Computers/Programming/Languages/Python/Books/",
        "http://www.dmoz.org/Computers/Programming/Languages/Python/Resources/"
    ]

    # def parse(self, response):
    #     filename = response.url.split("/")[-2]
    #     with open(filename, 'wb') as f:
    #         f.write(response.body)

    # def parse(self, response):
    #     for sel in response.xpath('//ul/li'):
    #         title = sel.xpath('a/text()').extract()
    #         link = sel.xpath('x/@href').extract()
    #         desc = sel.xpath('text()').extract()
    #         print(title, link, desc)

    def parse(self, response):
        for sel in response.xpath('//ul/li'):
            item = DmozItem()
            item['title'] = sel.xpath('a/text()').extract()
            item['link'] = sel.xpath('x/@href').extract()
            item['desc'] = sel.xpath('text()').extract()
            yield item
