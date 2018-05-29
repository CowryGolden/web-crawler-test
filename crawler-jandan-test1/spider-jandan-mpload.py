#!/usr/bin/env python3
# -*- coding: utf-8 -*-

r'''
    # 解密图片下载地址后，使用多线程下载图片
    爬取[煎蛋网的妹子图](http://jandan.net/ooxx/page-44)指定页的图片——解密图片地址，然后使用多线程下载图片；具体分析如下：
    【首先说明一下，之前煎蛋网之所以增加了反爬虫机制，应该就是因为有太多的人去爬他们的网站了。爬虫频繁的访问网站会给网站带来压力，所以，建议大家写爬虫简单的运行成功就适可而止，不要过分地去爬别人的东西。】
        步骤一：爬取煎蛋网的妹子图，我们首先要打开任意一个妹子图的页面，比如 http://jandan.net/ooxx/page-44#comments ；
                然后，我们需要请求这个页面，获取2个关键的信息（后续会说明信息的具体作用），其中第一个信息是每个妹子图片的 hash 值，这个是后续用来解密生成图片地址的关键信息。
        步骤二：在页面中除了提取到图片的 hash 之外，还有提取到当前页的一个关键的 js 文件的地址，这个 js 文件中包含了一个同样是用来生成图片地址的关键参数，
                要得到这个参数，必须去请求这个 JS 地址，当时妹子图的每个页面的 js 地址是不同的，所以需要从页面中提取。
        步骤三：得到了图片的 hash 和 js 中的关键参数之后，可以根据 js 中提供的解密方式，得到图片的链接，这个解密方式后续用 Python 代码和 js 代码的参照来说明。
        步骤四：有了图片链接，下载图片就不多说了，后续会有第二篇文章，来使用多线程+多进程的方式下载图片。

'''

# 导入资源
import requests
from bs4 import BeautifulSoup
import os, hashlib, re, base64, time, random
import threading, multiprocessing
import socket


def _md5(value):
    ''' md5加密 '''
    m = hashlib.md5()
    m.update(value.encode('utf-8'))
    return m.hexdigest()

def _base64_decode(data):
    ''' base64解码，要注意源字符串长度报错问题 '''
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += '=' * missing_padding
    return base64.b64decode(data)

def _current_path():
    ''' 获取当前路径 '''
    return os.path.abspath('.')

def get_imgurl(m ,r='', d=0):
    ''' 解密获取图片的链接 '''
    e = "DECODE"
    q = 4
    r = _md5(r)
    o = _md5(r[0:0 + 16])
    n = _md5(r[16:16 + 16])
    l = m[0:q]
    c = o + _md5(o + l)
    m = m[q:]
    k = _base64_decode(m)
    h = list(range(256))
    b = [ord(c[g % len(c)]) for g in range(256)]

    f = 0
    for g in range(0, 256):
        f = (f + h[g] + b[g]) % 256
        tmp = h[g]
        h[g] = h[f]
        h[f] = tmp

    t = ""
    p, f = 0, 0
    for g in range(0, len(k)):
        p = (p + 1) % 256
        f = (f + h[p]) % 256
        tmp = h[p]
        h[p] = h[f]
        h[f] = tmp
        t += chr(k[g] ^ (h[(h[p] + h[f]) % 256]))
    # t = t[26:]
    if e == "DECODE":
        t = _base64_decode(m).decode('utf-8')
    else:
        t = t[26:]    

    return t

def get_r(js_url):
    ''' 获取关键字符串 '''
    js = requests.get(js_url).text
    # 之前是使用下面注释的这个，后来煎蛋改了这个函数的名称
    # _r = re.findall('c=f_[\w\d]+\(e,"(.*?)"\)', js)[0]
    _r = re.findall('c=[\w\d]+\(e,"(.*?)"\)', js)[0]
    return _r

def load_img(imgurl, filepath):
    ''' 下载单张图片到指定的的文件夹下 '''
    start = time.time()
    time.sleep(random.random() * 2)    # 避免请求太频繁
    image_name = imgurl.split('/')[-1]
    filename = os.path.join(filepath, image_name)
    # headers = {'Referer': imgurl, 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}
    headers = {'Referer': imgurl, 'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:49.0) Gecko/20100101 Firefox/49.0'}
    print('正在下载图片（%s），其进程ID为：%s，父进程ID为：%s。' % (image_name, os.getpid(), os.getppid()))
    content = requests.get(imgurl,headers=headers).content
    with open(filename, 'wb') as f:
        f.write(content)
    end = time.time()
    print('图片（%s）下载完成。耗时：%.2f 秒。' % (image_name, end - start))



def load_imgs_bypage(url, filepath):
    ''' 多线程下载单页的所有图片 '''
    threads = []
    headers = {
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Host' : 'jandan.net'
    }
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, 'lxml')
    # js_url = 'http:' + re.findall('<script src="(//cdn.jandan.net/static/min/[\w\d]+\.\d+\.js)"><script>', html)[-1]    # 源代码中有两处的可以匹配，第一个注释，取最后一个
    js_sub_url = re.findall('<script src="(//cdn.jandan.net/static/min/[\w\d]+\.\d+\.js)"></script>', html)
    if len(js_sub_url) > 1:
        js_url = 'http:' + js_sub_url[-1]
    else:        
        js_url = 'http:' + js_sub_url[0]
    # print('js_url =', js_url)
    _r = get_r(js_url)    
    tags = soup.select('.img-hash')
    for tag in tags:
        img_hash = tag.text
        img_url = 'http://w' + get_imgurl(img_hash, _r)
        t = threading.Thread(target=load_img, args=(img_url, filepath))
        threads.append(t)
    for thread in threads:
        thread.start()
    for thread in threads:
        thread.join()
    print('URL = %s 整个网页图片下载完成。' % url)    


def load_imgs_pages_batch(start_page, end_page, filepath):
    ''' 多进程下载多页的图片
        传入的参数为：
            start_page: 起始页码
            end_page:   结束页码
            filepath:   图片保存的路径
    '''
    print('开始多进程批量下载第%s-%s页图片，其进程ID为：%s，其父进程ID为：%s。' % (start_page, end_page, os.getpid(), os.getppid()))
    pool = multiprocessing.Pool(processes=4)
    base_url = 'http://jandan.net/ooxx/page-{}'
    for i in range(start_page, end_page + 1):
        url = base_url.format(i)
        pool.apply_async(func=load_imgs_bypage, args=(url, filepath))
    pool.close()
    pool.join()


if __name__ == '__main__':
    page_numbers = input('请输入需要爬取的起止页码，形如（23-25）：')
    pages = page_numbers.split('-')
    start_page = int(pages[0])
    end_page = int(pages[1])
    # 这里省略 start_page 和 end_page 的有效性判断
    
    start = time.time()
    socket.setdefaulttimeout(20)    # 设置整个socket层的超时时间为20秒，后续文件中如果再使用到socket，不必再设置
    filepath = os.path.join(_current_path(), 'images')
    print('启动多进程批量下载图片任务，图片下载路径为（%s），其进程ID为：%s。' % (filepath, os.getpid()))
    load_imgs_pages_batch(start_page, end_page, filepath)
    end = time.time()
    print('多进程批量下载图片任务完成，共耗时%.2f秒。' % (end - start))




