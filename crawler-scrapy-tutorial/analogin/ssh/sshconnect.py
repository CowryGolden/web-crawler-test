#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''
    本程序目的：Python通过paramiko第三方库实现SSH连接，从而执行shell命令从服务器上传或下载文件到本地；
    参考文章链接：http://www.tendcode.com/article/python-ssh/
    本程序设计思路：
        1、首先创建一个配置文件，用来存放登录服务器的一些参数，例如服务器 host，端口 port，用户名称和密码等。
        2、读取配置文件的信息，返回一个字典以备后续调用
        3、使用 SSH 链接服务器，并且执行几个 shell 命令，返回需要下载的文件的绝对地址列表
        4、连接 SFTP 批量下载文件到本地
'''
__author__ = 'Cowry Golden'

# 导入依赖
import paramiko
import os
from configparser import ConfigParser


def read_config_ini():
    '''
    读取配置文件获取服务器登录信息
        :return: 返回配置文件参数信息
    '''
    info = dict()
    config = ConfigParser()
    config.read('config.ini', encoding='utf-8')
    keys = config.options('ssh')
    for key in keys:
        info[key] = config.get('ssh', key)
    print('========================== [INFO]:config.ini >>>>', info)
    return info


def ssh_connect(host, port, username, password):
    '''
    连接服务器，执行shell命令并返回输出结果
        :param host: 服务器IP地址
        :param port: ssh连接端口：22
        :param username: 登录服务器用户名
        :param password: 登录服务器密码

        :return sql_list: sql文件列表
    '''
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    # 连接服务器
    try:
        ssh.connect(hostname=host, port=port, username=username, password=password)
    except Exception as e:
        print(e)
        return
    
    # 设置一个内部函数，执行shell命令并返回输出结果
    def run_shell(cmd):
        ssh_in, ssh_out, ssh_error = ssh.exec_command(cmd)
        result = ssh_out.read() or ssh_error.read()
        return result.decode().strip()
    
    # 获取指定文件夹的绝对路径
    cmd_get_path = 'cd /srv/awesome/www_bak/db;pwd'
    db_path = run_shell(cmd_get_path)

    # 获取指定文件夹中文件的名称，并跟上面得到的文件绝对路径组合起来
    cmd_get_sqls = 'cd /srv/awesome/www_bak/db;ls'
    sqls = run_shell(cmd_get_sqls)
    sql_list = ['{}/{}'.format(db_path, each) for each in sqls.split('\n')]
    print('========================== [INFO]:sql_list >>>>', sql_list)

    # 关闭连接
    ssh.close()
    return sql_list


def sftp_file_transfer(host, port, username, password, from_file, to_file):
    '''
    连接服务器进行文件传输
        :param host: 服务器IP地址
        :param port: ssh连接端口：22
        :param username: 登录服务器用户名
        :param password: 登录服务器密码
        :param from_file: 服务器要下载文件路径
        :param to_file: 文件下载路径
    '''
    transport = paramiko.Transport((host, port))
    try:
        transport.connect(username=username, password=password)
    except Exception as e:
        print(e)
        return
    sftp = paramiko.SFTPClient.from_transport(transport)

    # 将文件下载到本地，如果是上传使用 put
    sftp.get(from_file, to_file)
    transport.close()



if __name__ == '__main__':
    info = read_config_ini()
    h = info.get('host', None)
    p = int(info.get('port', None))    # 端口是int类型
    u = info.get('username', None)
    pw = info.get('password', None)
    files = ssh_connect(h, p, u, pw)

    download_path = 'F:\\ade\\download\\db'
    if files:
        for each in files:
            filename = each.split('/')[-1]
            sftp = sftp_file_transfer(h, p, u, pw, each, os.path.join(download_path, filename))
            print('========================== [INFO]: >>>> 文件 %s 下载成功' % filename)

