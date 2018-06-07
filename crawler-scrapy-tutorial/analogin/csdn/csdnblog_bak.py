#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''
    本程序目的：Python模拟登录并获取CSDN博客所有文章列表
    参考文章链接：https://www.jianshu.com/p/c20544c42b4a
'''
__author__ = 'Cowry Golden'

# 导入依赖
import requests
import re
from bs4 import BeautifulSoup
import urllib.parse as parse


class CsdnHelper(object):
    ''' 登录CSDN和列出所有文章的处理类 '''

    csdn_login_url = 'https://passport.csdn.net/account/login?ref=toolbar'
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        # 'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko'
    }
    blog_url = 'http://write.blog.csdn.net/postlist/'

    def __init__(self):
        self._session = requests.session()
        self._session.headers = CsdnHelper.headers

    def _prepare_login_form_data(self, username, password):
        ''' 从页面获取参数，准备提交表单 '''
        response = self._session.get(CsdnHelper.csdn_login_url)
        login_page = BeautifulSoup(response.text, 'lxml')
        login_form = login_page.find('form', id='fm1')

        # 该参数可以理解成每个需要登录的用户都有一个流水号。只有有了webflow发放的有效的流水号，用户才可以说明是已经进入了webflow流程。否则，没有流水号的情况下，webflow会认为用户还没有进入webflow流程，从而会重新进入一次webflow流程，从而会重新出现登录界面。
        lt = login_form.find('input', attrs={'name': 'lt'})['value']
        execution = login_form.find('input', attrs={'name': 'execution'})['value']
        eventId = login_form.find('input', attrs={'name': '_eventId'})['value']
        form = {
            'username': username,
            'password': password,
            'lt': lt,
            'execution': execution,
            '_eventId': eventId
        }        
        return form

    def _validate_redirect_url(self):
        ''' 验证重定向页面 '''
        response = self._session.get(CsdnHelper.blog_url)
        redirect_url = re.findall(r'var redirect = "(\S+)";', response.text)[0]
        self._session.get(redirect_url)

    def _get_blog_count(self):
        ''' 获取文章数和页数 '''
        self._validate_redirect_url()
        response = self._session.get(CsdnHelper.blog_url)
        blog_page = BeautifulSoup(response.text, 'lxml')
        span = blog_page.find('div', class_='page_nav').span
        print('=========================================== span.string >>>', span.string)
        pattern = re.compile(r'(\d+)条\s*共(\d+)页')
        result = pattern.findall(span.string)
        blog_count = int(result[0][0])
        page_count = int(result[0][1])
        return (blog_count, page_count)


    def login(self, username, password):
        ''' 登录主函数 '''
        form_data = self._prepare_login_form_data(username, password)
        response = self._session.post(CsdnHelper.csdn_login_url, data=form_data)
        # cookies = requests.utils.dict_from_cookiejar(self._session.cookies)
        print('=========================================== form_data >>>', form_data)
        print('=========================================== response.headers >>>', response.headers)
        print('=========================================== response.cookies >>>', requests.utils.dict_from_cookiejar(self._session.cookies))
        if 'UserNick' in response.cookies:
            nick = response.cookies['UserNick']
            print('=========================================== parse.unquote(nick) >>>', parse.unquote(nick))
        else:
            raise Exception('登录失败')
    
    def print_blogs(self):
        ''' 输出文章信息 '''
        blog_count, page_count = self._get_blog_count()
        for index in range(1, page_count + 1):
            url = f'http://write.blog.csdn.net/postlist/0/0/enabled/{index}'
            response = self._session.get(url)
            page = BeautifulSoup(response.text, 'lxml')
            links = page.find_all('a', href=re.compile(r'http://blog.csdn.net/zjc123zjc123/article/details/(\d+)'))
            print('=========================================== [info] >>>', f'----------第{index}页----------')
            for link in links:
                blog_name = link.string
                blog_url = link['href']
                print('=========================================== [info] >>>', f'文章名称:《{blog_name}》 文章链接:{blog_url}')


if __name__ == '__main__':
    csdn_helper = CsdnHelper()
    username = input("请输入CSDN用户名：")
    password = input("请输入CSDN密码：")
    csdn_helper.login(username, password)
    csdn_helper.print_blogs()
