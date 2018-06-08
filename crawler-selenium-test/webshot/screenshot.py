#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''
    本程序目的：使用selenium写的多进程全网页截图工具（使用无头浏览器PhantomJS，不能使用太高版本的selenium（3.8.0以上版本已经废弃）；安装支持版本：pip3 install selenium==2.48.0；其他的浏览器比如谷歌和火狐都只能单屏幕截图，无法做到整个网页的截图。）
    参考文章链接：http://www.tendcode.com/article/PhantomJS-screenshot/
'''
__author__ = 'Cowry Golden'

# 导入依赖
from selenium import webdriver
from selenium.webdriver.chrome.options import Options    # 使用Headless模式的Chrome；由于高版本的selenium中PhantomJS已废弃
import os, time
import multiprocessing as mp

def readtxt():
    '''
    读取txt文件，返回一个列表，每个元素都是一个元组；
    文件的格式是图片保存的名称加英文都喊加网页地址。
    具体参见urls.txt文件内容
    '''
    with open('urls.txt', 'r') as f:
        lines = f.readlines()
    urls = []
    for line in lines:
        try:
            thelist = line.strip().split(',')
            if len(thelist) == 2 and thelist[0] and thelist[1]:
                urls.append((thelist[0], thelist[1]))
        except:
            pass
    return urls

def get_dir():
    '''
    判断文件夹是否存在，如果不存在就创建一个
    '''
    filename = 'images'
    if not os.path.isdir(filename):
        os.makedirs(filename)
    return filename

def get_current_path():
    ''' 获取当前路径 '''
    return os.path.abspath('.')

def webshot(tup):
    '''
    网页截图
        :param tuple tup: (图片名称, 网页地址) 构成的元组
    '''
    # ---------------------------- 方法一(可以截全图) ------------------------------（https://www.jianshu.com/p/45f299f9bf7c）
    # 要想使用PhantomJS，不能使用太高版本的selenium（3.8.0以上版本已经废弃），安装支持版本：pip3 install selenium==2.48.0
    driver = webdriver.PhantomJS(executable_path='D:\\ProgramFiles\\PhantomJS211\\bin\\phantomjs.exe')    # 使用 selenium 去启动无头浏览器 PhantomJS 来进行整个网页的截图。(其他的浏览器比如谷歌和火狐都只能单屏幕截图，无法做到整个网页的截图。)
    # ---------------------------- 方法二(不能截全图，必须拼接才行) ------------------------------（https://www.cnblogs.com/zhuxiaoxi/p/8425686.html）
    # 经测试PhantomJS已经是废弃的（deprecated），得使用无头的Chrome or Firefox代替；（selenium\webdriver\phantomjs\webdriver.py:line-49 : please use headless versions of Chrome or Firefox instead）
    # 所以还是先弃用掉PhantomJS改用推荐的Headless Chrome比较好。Headless模式是Chrome 59中的新特征。要使用Chrome需要安装chromedriver。
    # options = Options()
    # options.add_argument('--headless')
    # options.add_argument('--ignore-certificate-errors')
    # options.add_argument('--ignore-ssl-errors')
    # options.add_argument('--disable-gpu')
    # driver = webdriver.Chrome(chrome_options=options)
    # ---------------------------- 方法三(不能截全图，必须拼接才行) ------------------------------（http://www.mamicode.com/info-detail-2193163.html）
    # chrome_options = webdriver.ChromeOptions()
    # chrome_options.set_headless()
    # chrome_options.add_argument('--ignore-certificate-errors')
    # chrome_options.add_argument('--ignore-ssl-errors')
    # chrome_options.add_argument('--disable-gpu')
    # driver = webdriver.Chrome(chrome_options=chrome_options)
    
    driver.maximize_window()
    # 返回网页高度的js代码
    js_height = 'return document.body.clientHeight'
    img_name = str(tup[0])
    link = tup[1]
    images_path = os.path.join(get_current_path(), 'images')
    try:
        driver.get(link)
        k = 1
        height = driver.execute_script(js_height)
        while True:
            if k * 500 < height:
                js_move = 'window.scrollTo(0, {})'.format(k * 500)
                driver.execute_script(js_move)
                time.sleep(0.2)
                height = driver.execute_script(js_height)
                k += 1
            else:
                break
        driver.save_screenshot(os.path.join(images_path, img_name + '.png'))
        print('================================ [INFO]:Get Images Process >>>> Process {} get one image!'.format(os.getpid()))
        time.sleep(0.1)
    except Exception as e:
        print('================================ [ERROR]:【image_name={}】截图失败 >>>>'.format(img_name), e)


if __name__ == '__main__':
    ''' 运行测试 '''
    start = time.time()
    get_dir()
    urls = readtxt()
    pool = mp.Pool()
    pool.map_async(func=webshot, iterable=urls)
    pool.close()
    pool.join()
    print('================================ [INFO]:Game Over >>>> 操作结束， 运行耗时{:.2f}秒。'.format(float(time.time() - start)))




