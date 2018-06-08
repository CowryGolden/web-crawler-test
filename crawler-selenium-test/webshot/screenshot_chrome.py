#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''
    本程序目的：selenium中谷歌和火狐等浏览器驱动都只能单屏幕截图，无法做到整个网页的截图。因此本程序进行单屏截图后再进行长图拼接
    参考文章链接：https://github.com/auv1107/PythonSpiderLibs/blob/master/WebDriverLib.py （https://www.jianshu.com/p/7ed519854be7）
                https://www.cnblogs.com/sparkling-ly/p/5466644.html
'''
__author__ = 'Cowry Golden'

# 导入依赖
from selenium import webdriver
from selenium.webdriver.chrome.options import Options    # 使用Headless模式的Chrome；由于高版本的selenium中PhantomJS已废弃
from selenium.webdriver.support import expected_conditions as EC
import selenium.webdriver.support.ui as ui
import os, time
import multiprocessing as mp
from PIL import Image


class WebDriverScreenShotLib(object):
    '''
    selenium模拟谷歌或火狐浏览器进行单屏截图；PhantomJS无头浏览器可以进行滚动截屏
    '''
    def __init__(self, driver):
        self.wait = ui.WebDriverWait(driver, timeout=10)

    def waitToFind(self, by):
        return self.wait.until(
            EC.presence_of_element_located(by)
        )

    def waitToVisible(self, by):
        return self.wait.until(
            EC.visibility_of_element_located(by)
        )

    def waitToLeave(self, by):
        return self.wait.until(
            EC.invisibility_of_element_located(by)
        )

    def take_screenshot_on_element(self, driver, element, path='images', delay=2, padding=60):
        '''
        根据HTML中的元素进行截屏（适用于任何浏览器驱动）
            :param driver - 浏览器驱动
            :param element - html元素对象比如body，div，span等
            :param path - 保存图片的路径
            :param delay - 延迟的时间，以秒为单位
            :param padding - css中box的padding值，单位px
        '''
        check_and_mkdir(path)
        # time.sleep(10)
        driver.execute_script("arguments[0].scrollIntoView();", element)
        driver.execute_script("""
            (function () {
                var y = scrollY;
                var step = 100;
                window.scroll(0, y);
                function f() {
                    if (y < arguments[0]) {
                        y += step;
                        window.scroll(0, y);
                        setTimeout(f, 100);
                    } else {
                        document.title += "scroll-done";
                    }
                }
                setTimeout(f, 1000);
            })();
        """, element.location['y']+element.size['height'])

        for i in range(300):
            if "scroll-done" in driver.title:
                break
            time.sleep(1)

        print('Wait',delay,'seconds for images loading...')
        time.sleep(delay)
        print('Scroll to element.')
        location = element.location
        size = element.size
        window_size = driver.get_window_size()

        from selenium.webdriver.common.by import By
        body_height = driver.find_element(By.TAG_NAME, "body").size['height']

        remain_height = size['height']
        window_height = window_size['height'] - 80    # 此处每一屏的高度为屏幕的高度减去padding值
        step = window_height
        # padding = 60
        left = location['x'] - padding
        right = location['x'] + size['width'] + padding
        top = location['y']
        cur_bottom = location['y']
        screenshot_index = 0
        if remain_height <= window_height:
            filename = os.path.join(path, 'screenshot'+str(screenshot_index)+'.png')
            if top > window_height - size['height']:
                # scroll to put element at the bottom of window
                driver.execute_script("scroll(0,arguments[0]);", top + size['height'] - window_height)
                driver.save_screenshot(filename) # saves screenshot of entire page
                scop_to(filename, left, window_height-size['height'], right, window_height)
            else:
                driver.save_screenshot(filename) # saves screenshot of entire page
                scop_to(filename, left, element.location['y'], right, element.location['y'] + size['height'])
        else:
            driver.execute_script("arguments[0].scrollIntoView();", element)
            shots_images = check_and_mkdir(os.path.join(path, 'shots'))    # 长图分屏截图保存目录
            imageslist = []
            while True:
                time.sleep(0.1)
                print('Location size:',element.location['x'],element.location['y'],element.size['width'],element.size['height'])
                filename = os.path.join(shots_images, 'screenshot_'+str(screenshot_index)+'.png')
                driver.save_screenshot(filename) # saves screenshot of entire page
                imageslist.append(filename)
                remain_height -= step    # 全网页剩余高度 -= 每次截屏高度（步长）
                if remain_height <= 0:    # 此时remain_height=0成立（line:123-124重置step = remain_height），也就是说条件(remain_height <= 0)只可能=0成立
                    scop_to(filename, left, window_height-step, right, window_height)
                    # scop_to(filename, left, window_height-step, right, step)    # 此处80px为line:88屏幕高度padding
                    print('Save:',filename)
                    break
                else:
                    scop_to(filename, left, 0, right, step)
                if remain_height < step:
                    step = remain_height
                driver.execute_script("scrollBy(0,arguments[0]);", step)
                screenshot_index += 1
                cur_bottom += step                
                print('Save:',filename)
        driver.execute_script("document.title = document.title.replace('scroll-done','')")
        print('Starting to merge images...')
        image_merge(imageslist, path, 'screenshot_merge_all.png')
        print('Merge screenshot images successufully.')

    def take_screenshot_on_item(self, driver, item, path='images'):
        '''
        截取屏幕全图（如果有垂直滚动条，只适用于PhantomJS无头浏览器）
            :param driver - 浏览器驱动
            :param item - html元素对象比如body，div，span等
            :param path - 保存图片的路径
        '''
        check_and_mkdir(path)
        filename = os.path.join(path, 'screenshot.png')
        driver.save_screenshot(filename)
        left = item.location['x']
        right = left + item.size['width']
        top = item.location['y']
        bottom = top + item.size['height']
        scop_to(filename, left, top, right, bottom)

    def wait_for_img_loading_finished(self, driver, delay=2):
        '''
        执行滚动屏幕js代码，将网页全部加载完成，避免屏幕内容没有加载截图内容异样的问题；
            :param driver - 浏览器驱动
            :param delay - 延迟时间，单位为秒
        '''
        # driver.execute_script("arguments[0].scrollIntoView();")
        driver.execute_script("""
            (function () {
                var y = scrollY;
                var step = 100;
                window.scroll(0, 0);
                function f() {
                    if (y < document.body.scrollHeight) {
                        y += step;
                        window.scroll(0, y);
                        setTimeout(f, 100);
                    } else {
                        window.scroll(0,0);
                        document.title += "scroll-done";
                    }
                }
                setTimeout(f, 1000);
            })();
        """)

        for i in range(300):
            if "scroll-done" in driver.title:
                break
            time.sleep(1)
        time.sleep(delay)
   

def image_merge(images, output_dir, output_name='merge.jpg', restriction_max_width=None, restriction_max_height=None):  
    """
    垂直合并多张图片 
        :param images - 要合并的图片路径列表(list)
        :param ouput_dir - 输出路径 
        :param output_name - 输出文件名 
        :param restriction_max_width - 限制合并后的图片最大宽度，如果超过将等比缩小 
        :param restriction_max_height - 限制合并后的图片最大高度，如果超过将等比缩小 

        :return save_path - 输出文件名称
    """  
    def image_resize(img, size=(1500, 1100)):  
        """ 调整图片大小 """  
        try:  
            if img.mode not in ('L', 'RGB'):  
                img = img.convert('RGB')  
            img = img.resize(size)  
        except Exception as e:  
            pass  
        return img 
    max_width = 0  
    total_height = 0  
    # 计算合成后图片的宽度（以最宽的为准）和高度  
    for img_path in images:  
        if os.path.exists(img_path):  
            img = Image.open(img_path)  
            width, height = img.size  
            if width > max_width:  
                max_width = width  
            total_height += height  
  
    # 产生一张空白图  
    new_img = Image.new('RGB', (max_width, total_height), 255)  
    # 合并图片 
    x = y = 0  
    for img_path in images:  
        if os.path.exists(img_path):  
            img = Image.open(img_path)  
            width, height = img.size  
            new_img.paste(img, (x, y))  
            y += height  
  
    if restriction_max_width and max_width >= restriction_max_width:  
        # 如果宽带超过限制  
        # 等比例缩小  
        ratio = restriction_max_height / float(max_width)  
        max_width = restriction_max_width  
        total_height = int(total_height * ratio)  
        new_img = image_resize(new_img, size=(max_width, total_height))  
  
    if restriction_max_height and total_height >= restriction_max_height:  
        # 如果高度超过限制  
        # 等比例缩小  
        ratio = restriction_max_height / float(total_height)  
        max_width = int(max_width * ratio)  
        total_height = restriction_max_height  
        new_img = image_resize(new_img, size=(max_width, total_height))  
      
    if not os.path.exists(output_dir):  
        os.makedirs(output_dir)  
    save_path = os.path.join(output_dir, output_name)    # '%s/%s' % (output_dir, output_name)  
    new_img.save(save_path)  
    for img_path in images:     # 合并后将原始图片删除
        os.remove(img_path)
        # pass
    return save_path
    

def scop_to(filename, left, top, right, bottom):
    '''
    截图屏幕图片
        :param filename - 图片路径
        :param left - 要截取图片左上角顶点距屏幕左边的距离
        :param top - 要截取图片左上角顶点距屏幕顶部的距离
        :param right - 要截取图片左上角顶点向右边水平延伸的距离（图片宽度 = right - left）
        :param bottom - 要截取图片左上角顶点向下边垂直延伸的距离（图片高度 = bottom - top）
    '''  
    im = Image.open(filename) # uses PIL library to open image in memory
    im = im.crop((left, top, right, bottom)) # defines crop points
    im.save(filename) # saves new cropped image
    print('Crop:', filename)

def get_current_path():
    ''' 获取当前路径 '''
    return os.path.abspath('.')

def check_and_mkdir(filename):
    '''
    检查文件路径是否存在，不存在则创建
        :param filename - 文件路径
    '''
    if not os.path.isdir(filename):
        os.mkdir(filename)
    return filename        






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



if __name__ == '__main__':
    ''' 运行测试 '''
    start = time.time()

    options = Options()
    options.add_argument('--headless')
    options.add_argument('--ignore-certificate-errors')
    options.add_argument('--ignore-ssl-errors')
    options.add_argument('--disable-gpu')
    driver = webdriver.Chrome(chrome_options=options)

    driver.get('http://jandan.net/ooxx/page-50689497#comments')
    element = driver.find_element_by_tag_name('body')
    screenshot = WebDriverScreenShotLib(driver)
    screenshot.take_screenshot_on_element(driver, element)

    print('================================ [INFO]:Game Over >>>> 操作结束， 运行耗时{:.2f}秒。'.format(float(time.time() - start)))




