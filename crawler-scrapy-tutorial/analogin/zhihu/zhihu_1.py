#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''
    本程序目的：Python模拟登录新版知乎（验证成功）
    参考文章链接：https://mp.weixin.qq.com/s?__biz=MzUxNTI3NDYxNw==&mid=2247483690&idx=1&sn=c1b931cedd6b33e903e43c013ba77219&chksm=f9b8633ccecfea2a
'''
__author__ = 'Cowry Golden'

# 导入依赖  
import requests
import os, time, re
import base64, hmac, hashlib
import json
import matplotlib.pyplot as plt
from http import cookiejar
from PIL import Image
from bs4 import BeautifulSoup
import urllib.parse as parse
import inspect

HEADERS = {
    'Connection': 'keep-alive',
    'Host': 'www.zhihu.com',
    'Referer': 'https://www.zhihu.com/',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36'
}
LOGIN_URL = 'https://www.zhihu.com/signin'
LOGIN_API = 'https://www.zhihu.com/api/v3/oauth/sign_in'
PERSONAL_CENTER_URL = 'https://www.zhihu.com/settings/profile'
FORM_DATA = {
    'client_id': 'c3cef7c66a1843f8b3a9e6a1e3160e20',
    'grant_type': 'password',
    'source': 'com.zhihu.web',
    'username': '',
    'password': '',
    # 改为'cn'是倒立汉字验证码
    'lang': 'en',
    'ref_source': 'other_'
}

def get_current_function_name():
    '''
    利用inspect模块动态获取当前运行的函数名
        :return: 返回当前运行的函数名
    '''
    return inspect.stack()[1][3]


# 模拟登录知乎（新版）
class AnalogZhihuLogin(object):
    '''
    模拟登录知乎（新版）
    '''
    def __init__(self):
        self.login_url = LOGIN_URL
        self.login_api = LOGIN_API
        self.login_data = FORM_DATA.copy()
        self.session = requests.session()
        self.session.headers = HEADERS.copy()
        self.session.cookies = cookiejar.LWPCookieJar(filename='cookies.txt')
        self.personal_center_url = PERSONAL_CENTER_URL
    
    def login(self, username=None, password=None, load_cookies=True):
        '''
        模拟登录知乎：
            :param username: 登录手机号或邮箱
            :param password: 登录密码
            :param load_cookies: 是否读取上次保存的cookies
            :return type: bool(是否登录成功)
        '''
        if load_cookies and self.load_cookies():
            if self.check_login():
                return True
        
        headers = self.session.headers.copy()
        headers.update({
            'authorization': 'oauth c3cef7c66a1843f8b3a9e6a1e3160e20',
            'X-Xsrftoken': self._get_token()
        })
        username, password = self._check_user_passwd(username, password)
        self.login_data.update({
            'username': username,
            'password': password
        })
        timestamp = str(int(time.time() * 1000))
        self.login_data.update({
            'captcha': self._get_captcha(headers),
            'timestamp': timestamp,
            'signature': self._get_signature(timestamp)
        })
        response = self.session.post(self.login_api, data=self.login_data, headers=headers)
        if 'error' in response.text:
            print(re.findall(r'"message":".+?"', response.text)[0])
        elif self.check_login():
            return True
        print('登录失败')
        return False
    
    def load_cookies(self):
        '''
        读取cookies文件加载到session中：
            :return type: bool(是否加载成功)
        '''
        try:
            self.session.cookies.load(ignore_discard=True)
            return True
        except IOError as e:
            return False

    def check_login(self):
        '''
        检查登录状态，访问登录页面出现跳转则已是登录，
        如登录成功则保存当前cookies
            :return type: bool(是否成功)
        '''
        response = self.session.get(self.login_url, allow_redirects=False)    # 禁止重定向，否则登录失败重定向到首页也是响应200
        if response.status_code == 302:    # 302 redirect:：302代表暂时性转移(Temporarily Moved )
            self.session.cookies.save()
            print('登录成功')
            print('================================= [INFO]：登录成功后重定向URL >>>>', response.text)    # Redirecting to <a href="https://www.zhihu.com">https://www.zhihu.com</a>.
            return True
        return False

    def _get_token(self):
        '''
        从登录页面获取token
            :return: token
        '''
        response = self.session.get(self.login_url)
        token = re.findall(r'_xsrf=([\w|-]+)', response.headers.get('Set-Cookie'))[0]    # 查看网页Network中第一次请求api=https://www.zhihu.com/api/v3/oauth/captcha?lang=en 的Response中的内容
        return token


    def _get_captcha(self, headers):
        '''
        请求验证码的 API 接口，无论是否需要验证码都需要请求一次
        如果需要验证码会返回图片的 base64 编码
        根据头部 lang 字段匹配验证码，需要人工输入
            :param headers: 带授权信息的请求头部
            :return: 验证码的 POST 参数
        '''
        lang = headers.get('lang', 'en')
        if lang == 'cn':
            api = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=cn'
        else:
            api = 'https://www.zhihu.com/api/v3/oauth/captcha?lang=en'
        response = self.session.get(api, headers=headers)
        show_captcha = re.search(r'true', response.text)
        if show_captcha:
            put_resp = self.session.put(api, headers=headers)
            img_base64 = re.findall(r'"img_base64":"(.+)"', put_resp.text, re.S)[0].replace(r'\n', '')
            with open('./captcha.jpg', 'wb') as f:
                f.write(base64.b64decode(img_base64))
            img = Image.open('./captcha.jpg')
            if lang == 'cn':
                plt.imshow(img)
                print('点击所有倒立的汉字，按回车提交')
                points = plt.ginput(7)
                captcha = json.dumps({
                    'img_size': [200, 44],
                    'input_points': [[i[0]/2, i[1]/2] for i in points]
                })
            else:
                img.show()
                captcha = input('请输入图片里的验证码：')
            # 这里必须先把参数POST到验证码接口
            self.session.post(api, data={'input_text': captcha}, headers=headers)
            return captcha
        return ''
    
    def _get_signature(self, timestamp):
        '''
        通过Hmac算法计算返回签名参数，
        实际就是几个固定字符串参数再加时间戳的哈希算法
            :param timestamp: 时间戳
            :return: 签名参数字符串
        '''
        ha = hmac.new(b'd1b964811afb40118a12068ff74a12f4', digestmod=hashlib.sha1)
        grant_type = self.login_data['grant_type']
        client_id = self.login_data['client_id']
        source = self.login_data['source']
        ha.update(bytes((grant_type + client_id + source + timestamp), encoding='utf-8'))
        return ha.hexdigest()

    def _check_user_passwd(self, username, password):
        '''
        检查用户名和密码是否已输入，若无则手动输入
            :return: username, password
        '''
        if username is None:
            username = self.login_data.get('username')
            if not username:
                username = input('请输入知乎账号：')
        if re.match(r'\d{11}$', username):
            if '+86' not in username:
                username = '+86' + username
        if password is None:
            password = self.login_data.get('password')       
            if not password:
                password = input('请输入知乎密码：')
        return username, password

    def get_personal_info(self):
        '''
        登录成功后，访问个人中心获取信息
            :return: 个人中心信息(用户名，个性域名等)
        '''
        print('================================= [INFO]：执行%s.%s() >>>> 获取个人中心信息开始...' % (self.__class__.__name__, get_current_function_name()))
        response = self.session.get(self.personal_center_url, headers=self.session.headers, allow_redirects=False)
        
        profile_page = BeautifulSoup(response.text, 'lxml')
        account_form = profile_page.find('form', id='js-settings-account-form')
        fullname = account_form.find('div', id='rename-section').find('span', attrs={'class': 'name'}).text    # 只有一个span，使用find('span')即可
        domain_url = os.path.join('zhihu.com/people/', account_form.find('div', id='js-url-preview').find('span').text)
        info = {
            'fullname': fullname,
            'domain_url': domain_url,
        }
        return info
        


if __name__ == '__main__':
    zhihu = AnalogZhihuLogin()
    if zhihu.login(username=None, password=None, load_cookies=False):
        info = zhihu.get_personal_info()
        print('================================= [INFO]：获取个人信息 >>>>', info)




