#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''
    本程序目的：.app域名发布了，使用Python爬虫查询那些大公司是否进行注册(生产者/消费者模型)
                Productor类是生产者，作用是读取URL并请求和解析网页，最后将提取到的信息存放到一个队列里面供消费者使用
                Worker类是消费者，作用是从队列拿信息，然后写入到文件中
                get_csv函数是一个生成表格文件的函数，它可以在爬虫每次运行的时候新生成一个表格，并且给表格添加指定的列标题
                main函数就不用多说了，它就是负责整个爬虫启动的函数，只需要传入一个文件的名称就行了
    参考文章链接：http://www.tendcode.com/article/spider-for-domain/
    设计思路：
        1、首先，我要知道有哪些大公司的域名是值得去查询的，这里我可以使用站长平台的网站排行榜（中国）里面的网站榜单（http://top.chinaz.com/all/），大概56700个网站，我可以爬取这些网站的信息，然后提取出域名的前一部分。
        2、当我拿到了大公司的域名之后，我可以把这些大公司的域名的顶级域名部分换成 .app，然后去批量查询这些公司的 .app 域名是否已经注册，并记录下还没有被注册的域名。
        3、队列（Queue）、多线程（threading）的使用，以及对生产者/消费者模型的实践。
'''
__author__ = 'Cowry Golden'

# 导入依赖
import requests
from lxml import etree
from threading import Thread, Lock
from queue import Queue
import os, re, time
import csv


class Productor(Thread):
    '''
    生产者，作用是读取URL并请求和解析网页，最后将提取到的信息存放到一个队列里供消费者使用
    '''
    def __init__(self, queue, worker_queue):
        '''
        生产者类初始化函数
            :param Queue queue: URL构成的“原料”队列
            :param Queue worker_queue: 存放网站信息的队列，供消费者使用
        '''
        Thread.__init__(self)
        self.queue = queue
        self.worker_queue = worker_queue
        self.session = requests.Session()
        # 这个地方很重要，不设置这个请求状态的话后续请求会报错
        self.session.keep_alive = False
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        }

    def run(self):
        '''
        生产者运行函数
        '''
        while not self.queue.empty():
            key = self.queue.get()
            url = key[0]
            if key[1] < 3:
                try:
                    response = self.session.get(url, headers=self.headers, timeout=2)
                    time.sleep(0.1)
                except Exception as e:
                    self.queue.put((url, key[1] + 1))
                    print('================================ [ERROR]:【url={}】第 {} 次访问失败，失败原因: >>>>'.format(url, key[1] + 1), e)
                else:
                    # 设置网页字符编码
                    response.encoding = 'utf-8'
                    self.get_info(response.text)
            else:
                # 每个链接最多请求3次，如果3次还失败就放弃请求，打印链接信息
                # 如果不这样设置的话，有的链接会请求一直超时造成死循环
                print('================================ [WARNING]:无法访问的链接 >>>>', key)
        print('================================ [INFO]:生产者线程 >>>> {} 线程结束'.format(self.getName()))
    
    def get_info(self, html):
        '''
        获取网页信息（http://top.chinaz.com/all/）
            :param str html: html文本字符串
        '''
        tree = etree.HTML(html)
        sites = tree.xpath('//ul[@class="listCentent"]/li')
        for site in sites:
            info = dict()
            name = site.xpath('.//h3[@class="rightTxtHead"]/a/text()')
            # 有一个网站没有名字，因此要判断查找是否为空
            name = name[0] if name else ''
            url = site.xpath('.//h3[@class="rightTxtHead"]/span/text()')[0]
            alexa = site.xpath('.//p[@class="RtCData"][1]/a/text()')[0]
            baidu_s = site.xpath('.//p[@class="RtCData"][2]/a/img/@src')[0]
            baidu_pr = site.xpath('.//p[@class="RtCData"][3]/a/img/@src')[0]
            baidu_fl = site.xpath('.//p[@class="RtCData"][4]/a/text()')[0]
            rank = site.xpath('.//div[@class="RtCRateCent"]/strong/text()')[0]
            score = site.xpath('.//div[@class="RtCRateCent"]/span/text()')[0]
            # 名字里面有特殊字符，所以可以过滤掉特殊字符
            info['name'] = name.encode('gbk', 'ignore').decode('gbk')
            info['url'] = url
            info['alexa'] = alexa
            info['baidu_s'] = self.get_str(baidu_s)
            info['baidu_pr'] = self.get_str(baidu_pr)
            info['baidu_fl'] = baidu_fl
            info['rank'] = rank
            info['score'] = score.replace('得分:', '')
            self.worker_queue.put(info)

    def get_str(self, url):
        '''
        从百度权重或PR的图片中提取权重值
            :param str url: 图片url
            :return str value: 权重值  
        '''
        value = re.findall(r'(\d+)\.gif', url)[0]
        return value


class Worker(Thread):
    '''
    消费者，作用是从队列拿信息，然后写入到文件中
    '''
    def __init__(self, worker_queue, filename, lock):
        '''
        消费者类初始化函数
        :param worker_queue: 存放网站信息的队列，供消费者使用
        :param filename: 文件名（可带文件路径）
        :param lock: 资源锁
        '''
        Thread.__init__(self)
        self.worker_queue = worker_queue
        self.filename = filename
        self.lock = lock

    def run(self):
        '''
        消费者运行函数
        '''
        while True:
            info = self.worker_queue.get()
            if info is None:
                break
            try:
                # 因为消费者/生产者模式共享资源，所以要加锁
                self.lock.acquire()    # 使用资源前，获取锁
                self.writeinfo(info)
                self.lock.release()    # 用完资源后，释放锁
            except Exception as e:
                print('================================ [ERROR]:数据【info={}】写入异常，异常原因: >>>>'.format(info), e)
                # print(info, e)
            self.worker_queue.task_done()
        print('================================ [INFO]:消费者线程 >>>> {} worker is done!'.format(self.getName()))

    def writeinfo(self, data):
        '''
        往文件中写数据
            :param data: 要写的数据内容
        '''
        headers = ['name', 'url', 'alexa', 'baidu_s', 'baidu_pr', 'baidu_fl', 'rank', 'score']
        with open(self.filename, 'a', newline='', encoding='gbk') as f:
            writer = csv.DictWriter(f, fieldnames=headers)
            writer.writerow(data)

def get_csv(filename):
    '''
    创建一个新的csv表格，并且设置标题
        :param filename: 文件名（可带文件路径）
    '''
    headers = ['name', 'url', 'alexa', 'baidu_s', 'baidu_pr', 'baidu_fl', 'rank', 'score']
    with open(filename, 'w', newline='', encoding='gbk') as f:
        writer = csv.DictWriter(f, fieldnames=headers)
        writer.writeheader()

def main(filename):
    '''
    运行主函数
        :param filename: 文件名（可带文件路径）
    '''
    get_csv(filename)
    lock = Lock()
    queue = Queue()    # URL构成的“原料”队列
    worker_queue = Queue()    # 存放网站信息的队列，供消费者使用
    # 插入的信息是链接和一个基础的请求次数0构成的元组，为了后续判断链接请求了几次
    queue.put(('http://top.chinaz.com/all/index.html', 0))
    baseurl = 'http://top.chinaz.com/all/index_{}.html'
    for i in range(2, 1894):    # 目前网站上共1894页
        queue.put((baseurl.format(i), 0))
    productorList = [Productor(queue, worker_queue) for i in range(10)]
    for productor in productorList:
        productor.start()
    workerList = [Worker(worker_queue, filename, lock) for i in range(5)]
    for worker in workerList:
        worker.start()
    for productor in productorList:
        productor.join()
    worker_queue.join()
    for worker in workerList:
        worker_queue.put(None) 
    for worker in workerList:
        worker.join()
    print('================================ [INFO]:Game Over >>>> 程序运行结束！')

if __name__ == '__main__':
    main('info.csv')



