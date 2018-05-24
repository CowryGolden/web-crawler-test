#!/usr/bin/env python3
# -*- coding: utf-8 -*-
r'''
    本程序目的：读取数据文件进行画折线图
'''
__author__ = 'Cowry Golden'

# 导入依赖
import numpy as np  
import matplotlib.pyplot as plt 
import matplotlib as mpl
from os import path

with open(path.abspath(path.join(path.dirname(__file__), 'test_data.txt')), 'r', encoding='utf-8', errors='ignore') as f:
	s = f.read()
	li = eval(s)
	
for subli in li:
	subli[3] = round(subli[3]/10000, 1) #阅读量以万为单位，方便看图

#画图
mpl.rcParams['font.sans-serif'] = ['SimHei'] #用来正常显示中文标签

def plotline(x, xtext, y, savepath,fig=0):#fig解决虚线对不准的问题
	plt.figure() #创建绘图对象
	plt.ylim(0, 650)  
	plt.plot(x, y, "b", linewidth=4)  #当前绘图对象绘图（X轴，Y轴，蓝色实线，线宽度）  
	plt.xlabel("contents") #X轴标签  
	plt.xticks(x, xtext, rotation=90)
	plt.ylabel("阅读量（万）")  #Y轴标签  
	plt.title("Line plot") #图标题 
	#数据标签
	for a,b in zip(x,y): 
		plt.text(a, b+0.05, '%.0f' % b, ha='center', va= 'bottom', fontsize=14)
	#竖直虚线	
	for item in range(len(x)): 
			plt.vlines(item + fig, 0, y[item], colors = "b", linestyles = "dashed") 

	fig=plt.gcf()
	fig.set_size_inches(40,20)
	plt.show()  #显示图 
	fig.savefig(savepath,dpi=200) #保存图

x = [subli[0] for subli in li]  # X轴标度（序号）
xtext = [subli[1] for subli in li]  # X轴标签
y = [subli[3] for subli in li]  # Y轴标度（阅读量）
savepath1 = path.abspath(path.join(path.dirname(__file__), 'test_line1_byitem.png'))
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


x2 = [subli[4] for subli in li if subli[5]==0]  # X轴
xtext2 = [subli[1] for subli in li if subli[5]==0]  # X轴标签
y2 = [subli[3] for subli in li if subli[5]==0]  # Y轴 阅读量
savepath2 = path.abspath(path.join(path.dirname(__file__), 'test_line2_bychapter.png'))
plotline(x2, xtext2, y2,savepath2, 1)


