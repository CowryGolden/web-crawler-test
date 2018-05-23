#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''
    本程序目的：使用爬虫收集《廖雪峰Python教程》中每一篇文章的阅读量,并做成折线图
'''
__author__ = 'Cowry Golden'

# 导入依赖
import requests
from bs4 import BeautifulSoup
from selenium import webdriver
import re
import time
from os import path
import numpy as np  
import matplotlib.pyplot as plt 
import matplotlib as mpl

py2site = 'https://www.liaoxuefeng.com/wiki/001374738125095c955c1e6d8bb493182103fac9270762a000'
py3site = 'https://www.liaoxuefeng.com/wiki/0014316089557264a6b348958f449949df42a6d3a2e542c000'
testsite = "http://127.0.0.1:5000/"

#直接爬取时，每2S请求一个网页，8个之后就统统返回503 Service Unavailable，所以使用selenium
#设置ChromeDriver不加载图片
chrome_opt = webdriver.ChromeOptions()
prefs = {"profile.managed_default_content_settings.images":2}
chrome_opt.add_experimental_option("prefs",prefs)
# driver_path = 'C:\\Program Files (x86)\\Google\\Chrome\\Application\\chromedriver.exe'    # http://npm.taobao.org/mirrors/chromedriver/ 下载对应版本的驱动程序，放置好后将路径配置在环境变量中
driver_path = 'C:\\Users\\Golden Cowry\\AppData\\Local\\Google\\Chrome\\Application\\chromedriver.exe'    # http://npm.taobao.org/mirrors/chromedriver/ 下载对应版本的驱动程序，放置好后将路径配置在环境变量中
browser = webdriver.Chrome(executable_path=driver_path, chrome_options=chrome_opt)

browser.get(py3site)
html = browser.page_source
#print(html.encode('gbk','ignore'))
soup = BeautifulSoup(html, 'lxml')

#收集目录
#查看网页源代码发现，目录放在<ul id="x-wiki-index" class......</ul>之中，提取ul标签
ul = soup.find(name="ul", id="x-wiki-index")
if not ul:
	raise ValueError('ul is None，没找到目录')

li = []
#章节的名字和链接都在 <ul>之下的<a>标签中，如<a href="/wiki/0f7a......>Python数据类型</a>
#每个<a>标签的<div>的 depth="1" 表示目录层次
#提取a标签，得到章节的名称、depth、链接
for (i, tag) in enumerate(ul.find_all("a")):
	li.append([i, tag.get_text(), tag.parent.attrs['depth'], 'https://www.liaoxuefeng.com'+tag.attrs['href']])
#总章节数
nums = len(li)

#收集每一小节的阅读量
def get_num_read(href):
	#time.sleep(1) #不能爬太频繁
	browser.get(href)
	html = browser.page_source
    #章节的阅读量放在<span>中，如 <span>阅读: 1035435</span>或<span>Reads: 1035434</span>
	#直接用正则匹配
	m = re.search(r'<span>.*\s(\d+)</span>', html)
	if m:
		num = m.groups()[0]
		return int(num)
	return 0

for subli in li:
	subli.append(get_num_read(subli[3]))
	#打印进度
	print('%s/%s %s Done, num: %s' % (subli[0], nums, subli[1], subli[4]))

browser.close()
print("爬虫工作完成")

li = [[x[0], x[1], x[2], x[4]] for x in li] #舍弃网址


#分3层制作目录,方便制图, 方便章节分组查看数据
#第一个页面的depth = 0 ，改为1，少一层
li[0][2] = '1' 
#章节目录，按 章-节-小节 分3层
li = [subli + [0, 0, 0] for subli in li]
#将第一个页面设为第1章
li[0][4] = 1  #[1, 'Python教程', '0', 6062921, 1, 0, 0]

X = (subli[0] for subli in li) #序号
Y = (int(subli[2]) for subli in li) #depth

#开始编制章节目录，按 章-节-小节 3层
for (x, y) in zip(X, Y):
	if x != 0:
		if y == 1:
			li[x][4] = li[x-1][4] + 1 #章+1
		elif y == 2:
			li[x][4] = li[x-1][4]
			li[x][5] = li[x-1][5] + 1 #节+1
		elif y == 3:
			li[x][4] = li[x-1][4]
			li[x][5] = li[x-1][5]
			li[x][6] = li[x-1][6] + 1 #小节+1

#整理好的数据存入txt
with open(path.abspath(path.join(path.dirname(__file__), 'dealed_data.txt')), 'w') as f:
	f.write(str(li).encode('utf-8'))

#画图	
for subli in li:
	subli[3] = round(subli[3]/10000, 1) #阅读量以万为单位

mpl.rcParams['font.sans-serif'] = ['SimHei'] #用来正常显示中文标签

def plotline(x, xtext, y, savepath,fig=0):    # fig解决数据分组后虚线对不准的问题
	plt.figure() # 创建绘图对象
	plt.ylim(0, 650)  # Y轴范围   # plt.ylim(0, max([subli[3] for subli in li]))
	plt.plot(x, y, "b", linewidth=4)  #当前绘图对象绘图（X轴，Y轴，蓝色实线，线宽度）  
	plt.xlabel("contents") # X轴标签  
	plt.xticks(x, xtext, rotation=90) # X轴刻度标签
	plt.ylabel("阅读量（万）")  # Y轴标签  
	plt.title("Line plot") # 图标题 
	#数据标签
	for (a, b) in zip(x,y): 
		plt.text(a, b+0.05, '%.0f' % b, ha='center', va= 'bottom', fontsize=14)
	#竖直虚线	
	for item in range(len(x)): 
		plt.vlines(item + fig, 0, y[item], colors = "b", linestyles = "dashed") 
	fig = plt.gcf()
	fig.set_size_inches(40,20)
	plt.show()  #显示图 
	# fig.savefig(savepath, dpi=200) #保存图, 要注释上一句

x = [subli[0] for subli in li]  # X轴标度（这里为序号）
xtext = [subli[1] for subli in li]  # X轴刻度的标签
y = [subli[3] for subli in li]  # Y轴标度（阅读量）
savepath1 = path.abspath(path.join(path.dirname(__file__), 'line1_byitem.png'))
plotline(x, xtext, y, savepath1)

#按章制图
#返回第 i 章的subli的索引
def lookup(i):
	for index in range(len(li)):
		if li[index][4]==i and li[index][5]==0:
			return index	
#整理数据，同一章的阅读量求和
for subli in li:
	if not subli[5]==0:
		li[lookup(subli[4])][3] = li[lookup(subli[4])][3] + subli[3]

x2 = [subli[4] for subli in li if subli[5]==0]
xtext2 = [subli[1] for subli in li if subli[5]==0]
y2 = [subli[3] for subli in li if subli[5]==0]
savepath2 = path.abspath(path.join(path.dirname(__file__), 'line2_bychapter.png'))
plotline(x2, xtext2, y2,savepath2, 1)


