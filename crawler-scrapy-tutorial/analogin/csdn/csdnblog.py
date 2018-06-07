#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''
    本程序目的：Python模拟登录并获取CSDN博客所有文章列表
    参考文章链接：https://www.jianshu.com/p/c20544c42b4a
    未测试成功，新版CSDN有一个js文件fpv2.js为加密，无法破解，因此无法获知登录参数fkid的生成方案：
        由于新版CSND登录中需要post一个参数fkid，
        该参数在“https://csdnimg.cn/release/passport/history/js/apps/login.js?v=1.3.8”中的获取方案为“$(“#fkid“).val(SMSdk.getDeviceId());”，
        而该deviceId的获取是从一个加密的js：“https://static.fengkongcloud.com/fpv2.js”通过参数组装请求“https://fp.fengkongcloud.com/v2/web/profile?callback=XXX&organization=XXX...”接口而获得，
        而获得的deviceId再通过加密才能作为post的参数发送给服务器，从而完成登录；
        （难点：破解fpv2.js难度比较大；不破解该js无法知道deviceId得到后的加密算法，因此即使通过接口获取到deviceId也无法完成登录；因此重点在于获取明文js内容分析加密算法，及获取deviceId的报文组装规则是关键；）
'''
__author__ = 'Cowry Golden'

# 导入依赖
import requests
import re
from bs4 import BeautifulSoup
import urllib.parse as parse
from http import cookiejar


class CsdnHelper(object):
    ''' 登录CSDN和列出所有文章的处理类 '''

    csdn_login_url = 'https://passport.csdn.net/account/login'
    csdn_login_verify_url = 'https://passport.csdn.net/account/verify'
    headers = {
        'Connection': 'keep-alive',
        'Host': 'passport.csdn.net',
        'Referer': 'https://www.csdn.net/',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
    }
    blog_url = 'http://write.blog.csdn.net/postlist/'

    def __init__(self):
        self._session = requests.session()
        self._session.headers = CsdnHelper.headers.copy()
        self._session.cookies = cookiejar.LWPCookieJar(filename='csdn_cookies.txt')


    def login(self, username, password, load_cookies=True):
        '''
        模拟CSDN登录主函数
            :param username: 登录手机号或邮箱
            :param password: 登录密码
            :param load_cookies: 是否读取上次保存的cookies
            :return type: bool(是否登录成功)
        '''

        if load_cookies and self.load_cookies():
            if self.check_login():
                return True

        form_data = self._prepare_login_form_data(username, password)
        response = self._session.post(CsdnHelper.csdn_login_verify_url, data=form_data, headers=CsdnHelper.headers)
        # self.check_login()
        print('=========================================== response.headers >>>', response.headers)
        # if self.check_login():
        #     return True
        # print('登录失败')
        # cookies = requests.utils.dict_from_cookiejar(self._session.cookies)
        # print('=========================================== response.cookies >>>', requests.utils.dict_from_cookiejar(response.cookies))
        # if 'UserNick' in response.cookies:
        #     nick = response.cookies['UserNick']
        #     print('=========================================== parse.unquote(nick) >>>', parse.unquote(nick))
        # else:
        #     raise Exception('登录失败')

    def load_cookies(self):
        '''
        读取cookies文件加载到session中：
            :return type: bool(是否加载成功)
        '''
        try:
            self._session.cookies.load(ignore_discard=True)
            return True
        except IOError as e:
            return False

    def check_login(self):
        '''
        检查登录状态，访问登录页面出现跳转则已是登录，
        如登录成功则保存当前cookies
            :return type: bool(是否成功)
        '''
        response = self._session.get(CsdnHelper.csdn_login_url, headers=CsdnHelper.headers, allow_redirects=False)    # 禁止重定向，否则登录失败重定向到首页也是响应200
        print('================================= [INFO]：status_code >>>>', response.status_code)
        # if response.status_code == 302:     # 301 redirect:：301代表永久性转移(Permanently Moved)
        #     self._session.cookies.save(ignore_discard=True, ignore_expires=True)
        #     print('登录成功')
        #     print('================================= [INFO]：登录成功后重定向URL >>>>', response.text)    # Redirecting to <a href="https://www.zhihu.com">https://www.zhihu.com</a>.
        #     return True
        # return False


    def _prepare_login_form_data(self, username, password):
        '''
        从页面获取参数，准备提交表单
            :param username: 登录手机号或邮箱
            :param password: 登录密码
            :return form_data: form表单数据
        '''
        response = self._session.get(CsdnHelper.csdn_login_url)
        login_page = BeautifulSoup(response.text, 'lxml')
        login_form = login_page.find('form', id='fm1')

        # 该参数可以理解成每个需要登录的用户都有一个流水号。只有有了webflow发放的有效的流水号，用户才可以说明是已经进入了webflow流程。否则，没有流水号的情况下，webflow会认为用户还没有进入webflow流程，从而会重新进入一次webflow流程，从而会重新出现登录界面。
        lt = login_form.find('input', attrs={'name': 'lt'})['value']
        execution = login_form.find('input', attrs={'name': 'execution'})['value']
        eventId = login_form.find('input', attrs={'name': '_eventId'})['value']
        form_data = {
            'username': username,
            'password': password,
            'lt': lt,
            'execution': execution,
            '_eventId': eventId
        }        
        return form_data

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
    csdn_helper.login(username, password, load_cookies=False)
    # csdn_helper.print_blogs()
