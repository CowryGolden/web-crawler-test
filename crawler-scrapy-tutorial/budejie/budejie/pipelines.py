# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://doc.scrapy.org/en/latest/topics/item-pipeline.html

import pymysql
import scrapy.pipelines.images
from scrapy.pipelines.images import ImagesPipeline
from scrapy.http import Request

# budejie MySQL保存管道
class BudejieMysqlPipeline(object):
    def __init__(self):
        self.conn = pymysql.connect(host='127.0.0.1', port=3306, user='root', passwd='system', db='testdb', charset='utf8')        
        self.cursor = self.conn.cursor()
        self.cursor.execute('truncate table joke')
        self.conn.commit()
                

    def open_spider(self, spider):
        self.cursor = self.conn.cursor()
    
    def close_spider(self, spider):
        self.cursor.close()
        self.conn.close()


    def process_item(self, item, spider):
        try:
            self.cursor.execute('insert into joke(author, content) values(%s, %s)' , (item['username'], item['content']))
            self.conn.commit()
        except pymysql.Error:
            print('Error:(%s, %s)' % (item['username'], item['content']))
        return item


'''
# 对下载的图片进行重命名；如果要使用该图片重名管道在settings.py中将ITEM_PIPELINES中架构原有的'scrapy.pipelines.images.ImagesPipeline': 1 注释掉（不注掉会重复保留hash名文件），将该管道配置在其中即可；
具体配置如下：
ITEM_PIPELINES = {
    # 'scrapy.pipelines.images.ImagesPipeline': 1,    # 保存hash文件名，关于为什么会有full文件夹，可参见【D:\ProgramFiles\Python364\Lib\site-packages\scrapy\pipelines\images.py line:162】
    'budejie.pipelines.RawFilenameImagePipeline': 200,    # 重命名管道
    'budejie.pipelines.BudejieMysqlPipeline': 300,    # 保存到mysql管道
}

IMAGES_STORE = 'images'    # 保存的目录
'''
class RawFilenameImagePipeline(ImagesPipeline):
    # 重写父类该方法
    def file_path(self, request, response=None, info=None):
        if not isinstance(request, Request):
            url = request
        else:
            url = request.url
        start = url.rfind('/') + 1
        end = url.rfind('.')
        if end == -1:
            return f'full/{url[start:]}.jpg'
        else:
            return f'full/{url[start:end]}.jpg'

# mm131管道
class RefererImagePipeline(ImagesPipeline):
    # 重写父类该方法
    def get_media_requests(self, item, info):
        requests = super().get_media_requests(item, info)
        for req in requests:
            req.headers.appendlist('referer', item['referer'])
        return requests

# csdn blog 管道
class CsdnBlogBackupPipeline(object):
    # 重写
    def process_item(self, item, spider):
        dirname = 'blogs'
        import os
        import codecs
        if not os.path.exists(dirname):
            os.mkdir(dirname)
        with codecs.open(f'{dirname}{os.sep}{item["title"]}.md', 'w', encoding='utf-8') as f:
            f.write(item['content'])
            f.close()
        return item
