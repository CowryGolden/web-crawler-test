# python 3
# 本程序目的：使用爬虫收集《廖雪峰Python教程》中每一篇文章的阅读量,并做成折线图

## 工具：requests lxml BeautifulSoup selenium matplotlib (使用 pip3 install requests[lxml/bs4/selenium/matplotlib] 分别导入工具依赖包)

## 文件介绍：
* `crawler.py`完整爬虫程序、并画图，运行即得到结果
* `dealed_data.txt`整理爬虫所得数据，`crawler.py`输出
* `line1_byitem.png`每篇文章的阅读量折线图，`crawler.py`输出
* `line2_bychapter.png`按章汇总之后的阅读量折线图，`crawler.py`输出
* `drawline_bydata.py`单独画图程序，草稿用(观看生成图效果，注意输入数据文件编码为`utf-8`)