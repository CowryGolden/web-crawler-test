#!/usr/bin/env python3
# -*- coding: utf-8 -*-

r'''
    使用Scrapy从http://www.budejie.com/text/上爬取内容
'''
# 导入资源
import scrapy
from scrapy import Request, FormRequest
from budejie.items import BudejieItem, MeizituImageItem, Mm131ImageItem, CsdnBlogItem

class BudejieSpider(scrapy.Spider):
    """使用Scrapy百思不得姐段子的爬虫"""
    name = 'budejie'
    start_urls = ['http://www.budejie.com/text/']
    total_page = 2

    def parse(self, response):
        # 爬虫本体就这样写，唯一需要注意的就是段子可能分为好几行，这里我们要统一合并成一个大字符串。选择器的extract()方法默认会返回一个列表，哪怕数据只有一个也是这样。所以如果数据是单个的，使用extract_first()方法。
        current_page = int(response.css('a.z-crt::text').extract_first())
        lies = response.css('div.j-r-list >ul >li')
        for li in lies:
            bItem = BudejieItem()
            bItem['username'] = li.css('a.u-user-name::text').extract_first()
            bItem['content'] = '\n'.join(li.css('div.j-r-list-c-desc a::text').extract())
            # print(bItem)
            yield bItem
        if current_page < self.total_page:
            yield scrapy.Request(self.start_urls[0] + f'{current_page+1}')    

# http://www.meizitu.com 爬虫专用
class MeizituSpider(scrapy.Spider):
    name = 'meizitu'
    start_urls = ['http://www.meizitu.com/a/5501.html']

    def parse(self, response):
        yield MeizituImageItem(image_urls=response.css('div#picture img::attr(src)').extract())


# http://www.mm131.com 爬虫专用
class Mm131Spider(scrapy.Spider):
    name = 'mm131'
    
    start_urls = ['http://www.mm131.com/xinggan/3473.html',
                  'http://www.mm131.com/xinggan/2746.html',
                  'http://www.mm131.com/xinggan/3331.html']

    def parse(self, response):
        total_page = int(response.css('span.page-ch::text').extract_first()[1:-1])
        current_page = int(response.css('span.page_now::text').extract_first())
        item = Mm131ImageItem()
        item['image_urls'] = response.css('div.content-pic img::attr(src)').extract()
        item['referer'] = response.url
        yield item
        if response.url.rfind('_')  == -1:
            head, sep, tail = response.url.rpartition('.')
        else:
            head, sep, tail = response.url.rpartition('_')
        if current_page < total_page:
            yield scrapy.Request(head + f'_{current_page+1}.html')


# 备份CSDN Blog
class CsdnBlogBackupSpider(scrapy.Spider):
    name = 'csdn_backup'
    start_urls = ['https://passport.csdn.net/account/login']
    # base_url = 'http://write.blog.csdn.net/postlist/'
    # get_article_url = 'http://write.blog.csdn.net/mdeditor/getArticle?id='
    base_url = 'https://mp.csdn.net/postlist/'
    get_article_url = 'https://mp.csdn.net/mdeditor/'

    def __init__(self, name=None, username=None, password=None, **kwargs):
        super(CsdnBlogBackupSpider, self).__init__(name=name, **kwargs)
        if username is None or password is None:
            raise Exception('没有用户名和密码')
        self.username = username
        self.password = password

    def parse(self, response):
        lt = response.css('form#fm1 input[name="lt"]::attr(value)').extract_first()
        execution = response.css('form#fm1 input[name="execution"]::attr(value)').extract_first()
        eventid = response.css('form#fm1 input[name="_eventId"]::attr(value)').extract_first()
        return FormRequest.from_response(
            response,
            formdata={
                'username': self.username,
                'password': self.password,
                'lt': lt,
                'execution': execution,
                '_eventId': eventid
            },
            callback=self.redirect_to_articles
        )

    def redirect_to_articles(self, response):
        return Request(CsdnBlogBackupSpider.base_url, callback=self.get_all_articles)

    def get_all_articles(self, response):
        import re
        text = response.css('div.page_nav span::text').extract_first()
        if text is None:    # 无分页
            total_page = 1
            yield Request(CsdnBlogBackupSpider.base_url + f'list/all', callback=self.parse_article_links)
        else:
            total_page = int(re.findall(r'共(\d+)页', text)[0])
            for i in range(1, total_page + 1):
                yield Request(CsdnBlogBackupSpider.base_url + f'list/{i}', callback=self.parse_article_links)

    def parse_article_links(self, response):
        # article_links = response.xpath('//table[@id="lstBox"]/tr[position()>1]/td[1]/a[1]/@href').extract()
        # article_links = response.xpath("//div[@class='tab-content']/div/div[@class='article-list-item']/div/p/a/@href").extract() # css('p.article-list-item-txt a::text')
        article_links = response.css('p.article-list-item-txt a::text')
        print('+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++>>>>', article_links)
        last_index_of = lambda x: x.rfind('/')
        article_ids = [link[last_index_of(link) + 1:] for link in article_links]
        for id in article_ids:
            yield Request(CsdnBlogBackupSpider.get_article_url + f'{id}', callback=self.parse_article_content)

    def parse_article_content(self, response):
        import json
        obj = json.loads(response.body, encoding='UTF8')
        yield CsdnBlogItem(title=obj['data']['title'], content=obj['data']['markdowncontent'])


