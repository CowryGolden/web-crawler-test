#!/usr/bin/env python3
# -*- coding: utf-8 -*-

r'''
    多线程方式
    多线程爬取[清纯妹子图片网](http://www.mmjpg.com/)指定页的内容；具体分析如下：
    整体分析网站后（打开一个具体页面看网页源码），确定爬取的思路是任意网站分页→图集分页→图片下载页，用链接说明的话，就是：
        第一步：获取这个网址的response，[分页内容](http://www.mmjpg.com/home/2)，解析后提取图集的地址
        第二步：获取这个网址的response，[图集分页](http://www.mmjpg.com/mm/895/13)，解析后提取图片的下载地址
        第三步：下载图片，http://img.mmjpg.com/2017/895/14.jpg，（也就是获取二进制内容，然后在本地复刻一份）
    每一步都对应一个功能函数，这样思路就清晰了。

'''

# 导入资源
import os, time, random
import requests
from lxml import html
from multiprocessing import Pool
import socket

# 获取当前路径
def _current_path():
    return os.path.abspath('.')

def get_page_number(num):
    # time.sleep(1) #不能爬太频繁
    #构建函数，用来查找该页内所有图片集的详细地址。目前一页包含15组套图，所以应该返回包含15个链接的序列。
    url = 'http://www.mmjpg.com/home/' + num
    #构造每个分页的网址
    response = requests.get(url).content
    #调用requests库，获取二进制的相应内容。注意，这里使用.text方法的话，下面的html解析会报错，大家可以试一下。这里涉及到.content和.text的区别了。简单说，如果是处理文字、链接等内容，建议使用.text，处理视频、音频、图片等二进制内容，建议使用.content。
    selector = html.fromstring(response)
    #使用lxml.html模块构建选择器，主要功能是将二进制的服务器相应内容response转化为可读取的元素树（element tree）。lxml中就有etree模块，是构建元素树用的。如果是将html字符串转化为可读取的元素树，就建议使用lxml.html.fromstring，毕竟这几个名字应该能大致说明功能了吧。
    urls = []
    #准备容器
    for i in selector.xpath("//ul/li/a/@href"):
    #利用xpath定位到所有的套图的详细地址
        urls.append(i)
        #遍历所有地址，添加到容器中
    return urls
    #将序列作为函数结果返回


def get_image_title(url):
    #现在进入到套图的详情页面了，现在要把套图的标题和图片总数提取出来
    response = requests.get(url).content
    selector = html.fromstring(response)
    image_title = selector.xpath("//h2/text()")[0]
    #需要注意的是，xpath返回的结果都是序列，所以需要使用[0]进行定位
    return image_title

def get_image_amount(url):
    #这里就相当于重复造轮子了，因为基本的代码逻辑跟上一个函数一模一样。想要简单的话就是定义一个元组，然后把获取标题、获取链接、获取图片总数的3组函数的逻辑揉在一起，最后将结果作为元组输出。不过作为新手教程，还是以简单易懂为好吧。想挑战的同学可以试试写元组模式
    response = requests.get(url).content
    selector = html.fromstring(response)
    image_amount = selector.xpath("//div[@class='page']/a[last()-1]/text()")[0]
    # a标签的倒数第二个区块就是图片集的最后一页，也是图片总数，所以直接取值就可以
    return image_amount


def get_image_detail_website(url):
    #这里还是重复造轮子。
    response = requests.get(url).content
    selector = html.fromstring(response)
    image_detail_websites = []
    image_amount = selector.xpath("//div[@class='page']/a[last()-1]/text()")[0]
    #这里重复构造变量，主要是为了获取图片总数。更高级的方法是使用函数间的传值，但是我忘了怎么写了，所以用了个笨办法。欢迎大家修改
    #构建图片具体地址的容器
    for i in range(int(image_amount)):
        image_detail_link = '{}/{}'.format(url, i+1)
        response = requests.get(image_detail_link).content
        sel = html.fromstring(response)
        image_download_link = sel.xpath("//div[@class='content']/a/img/@src")[0]
        #这里是单张图片的最终下载地址
        image_detail_websites.append(image_download_link)
    return image_detail_websites

# 为防止反爬虫，增加请求headers（从浏览器的调试窗口Network中找到请求的Headers更新就可以了）
def header(referer):
    headers = {
        'Host': 'www.mmjpg.com',
        'Pragma': 'no-cache',
        'Accept-Encoding': 'gzip, deflate',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Referer': referer
    }
    return headers

# 下载单张图片
def download_image(imgurl, filename, info):
    print('下载图集（%s）>> 第%s/%s张，其进程ID为：%s，父进程为：%s。' % (info[0], info[1], info[2], os.getpid(), os.getppid()))
    start1 = time.time() 
    with open(filename, 'wb+') as f:
        header = {'Referer': imgurl, 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'}    # 加上此header反爬虫才能下载正常的图片
        print('正在下载图片：图集（%s）第%s/%s张，' % (info))
        f.write(requests.get(imgurl,headers=header).content)
        time.sleep(random.random() * 10)       
    end1 = time.time()
    print('下载图集（%s）>> 第%s/%s张，运行耗时：%.2f 秒' % (info[0], info[1], info[2], (end1 - start1)))


# 批量下载图集
def download_images_batch(pool, image_title, image_detail_websites):
    print('下载图集（%s），其进程ID为：%s，父进程为：%s。' % (image_title, os.getpid(), os.getppid()))
    start = time.time()
    # time.sleep(1) #不能爬太频繁
    #将图片保存到本地。传入的两个参数是图片的标题，和下载地址序列
    num = 1
    amount = len(image_detail_websites)
    #获取图片总数
    for imgurl in image_detail_websites:
        info = (image_title, num, amount)
        print('下载图集（%s）>> 第%s/%s张，其进程ID为：%s，父进程为：%s。' % (image_title, num, amount, os.getpid(), os.getppid()))                
        filename = os.path.join(os.path.join(_current_path(), 'images'), '%s%s.jpg' % (image_title, num))
        print('将下载图片：%s第%s/%s张，放入下载队列' % (image_title, num, amount))
        # download_image(imgurl, filename)
        pool.apply_async(download_image, args=(imgurl, filename, info))    # 此种方式是将每个图集的单个图片的下载作为子进程交由线程池管理，因此不会被远程机的反爬虫机制和谐掉
        num += 1
    end = time.time()
    print('下载图集（%s），运行耗时：%.2f 秒' % (image_title, (end - start)))    



if __name__ == '__main__':
    page_number = input('请输入需要爬取的页码：')
    print('开始下载图片，父进程ID为：%s。' % os.getpid())
    p = Pool(8)
    socket.setdefaulttimeout(20)    # 设置整个socket层的超时时间为20秒，后续文件中如果再使用到socket，不必再设置
    for link in get_page_number(page_number):
        # download_images_batch(get_image_title(link), get_image_detail_website(link))
        # p.apply_async(download_images_batch, args=(get_image_title(link), get_image_detail_website(link)))    # 该种方式仅仅将图集下载放到了线程池中，而每个图集中的单个图片下载不是多线程执行的，因此会被远程机的反爬虫机制和谐掉
        download_images_batch(p, get_image_title(link), get_image_detail_website(link))    # 此种方式是将每个图集的单个图片的下载作为子进程交由线程池管理，因此不会被远程机的反爬虫机制和谐掉
    
    print('等待所有子进程下载图片完成 ...')
    p.close()
    p.join()
    print('所有子进程下载图片完成，下载图片结束。')

