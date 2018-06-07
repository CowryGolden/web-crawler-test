#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''
    本程序目的：Python第三方插件selenium模拟登录知乎(验证成功)
'''
__author__ = 'Cowry Golden'

# 导入依赖  
from selenium import webdriver
import requests
import time


#利用selenium登录，获取cookies
br=webdriver.Chrome()
br.get("https://www.zhihu.com/#signin")
# br.find_element_by_xpath("//span[contains(text(),'使用密码登录')]").click()
# br.find_element_by_xpath("//input[@name='account']").send_keys("***********")
# br.find_element_by_xpath("//input[@name='password']").send_keys("***********")

br.find_element_by_xpath("//span[contains(text(),'登录')]").click()
br.find_element_by_xpath("//input[@name='username']").send_keys("***********")
br.find_element_by_xpath("//input[@name='password']").send_keys("***********")

time.sleep(5)#手工点击验证码倒立文字预留时间
br.find_element_by_xpath("//button[@type='submit' and contains(text(),'登录')]").click()
time.sleep(3)#网页加载时间
selenium_cookies=br.get_cookies()#把selenium获取的cookies保存到变量，备用。
# print(selenium_cookies)
br.quit()

#接下来由requests接收selenium的cookies，并访问网站
s=requests.Session()
for i in selenium_cookies:
    requests.utils.add_dict_to_cookiejar(s.cookies, {i['name']:i['value']})
headers={
    'Host':'www.zhihu.com',
    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
    'Accept-Language':'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
    'Accept-Encoding':'gzip, deflate, br',
    'Connection':'keep-alive',
    'Upgrade-Insecure-Requests':'1',
    'Pragma':'',
    'Cache-Control':'',
}
r=s.get("https://www.zhihu.com",headers=headers).content.decode('utf-8')
print(r)#访问个人中心验证
