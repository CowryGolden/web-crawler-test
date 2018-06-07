# 爬取[煎蛋网的妹子图](http://jandan.net/ooxx/page-44)指定页的图片——解密图片地址，煎蛋网妹子图的链接获取方式
> 首先说明一下，之前煎蛋网之所以增加了反爬虫机制，应该就是因为有太多的人去爬他们的网站了。爬虫频繁的访问网站会给网站带来压力，所以，建议大家写爬虫简单的运行成功就适可而止，不要过分地去爬别人的东西。

## 爬虫思路分析
>* 图片下载流程图

![图片下载流程图](https://i.imgur.com/eAR1nqY.png)

>* 流程图解读

    1. 爬取煎蛋网的妹子图，我们首先要打开任意一个妹子图的页面，比如`http://jandan.net/ooxx/page-44#comments`然后，我们需要请求这个页面，获取2个关键的信息（后续会说明信息的具体作用），其中第一个信息是每个妹子图片的 hash 值，这个是后续用来解密生成图片地址的关键信息。

    2. 在页面中除了提取到图片的 hash 之外，还有提取到当前页的一个关键的 js 文件的地址，这个 js 文件中包含了一个同样是用来生成图片地址的关键参数，要得到这个参数，必须去请求这个 JS 地址，当时妹子图的每个页面的 js 地址是不同的，所以需要从页面中提取。

    3. 得到了图片的 hash 和 js 中的关键参数之后，可以根据 js 中提供的解密方式，得到图片的链接，这个解密方式后续用 Python 代码和 js 代码的参照来说明。

    4. 有了图片链接，下载图片就不多说了，后续会有第二篇文章，来使用多线程+多进程的方式下载图片。

## 页面分析

>* 网页源代码解读

我们可以打开一个妹子图的页面，还是最开始的`http://jandan.net/ooxx/page-44#comments`为例，然后查看源代码（注意，不是审查元素），可以看到本应该放图片地址的地方并没有图片地址，而是类似于下面的代码：
```
<p>
    <img src="//img.jandan.net/img/blank.gif" onload="jandan_load_img(this)" />
    <span class="img-hash">ece8ozWUT/VGGxW1hlbITPgE0XMZ9Y/yWpCi5Rz5F/h2uSWgxwV6IQl6DAeuFiT9mH2ep3CETLlpwyD+kU0YHpsHPLnY6LMHyIQo6sTu9/UdY5k+Vjt3EQ</span>
</p>
```    
从这个代码可以看出来，图片地址被一个 js 函数代替了，也就是说图片地址是由这个jandan_load_img(this)函数来获取并加载的，所以，现在的关键是，需要到 JS 文件中查找这个函数的意义。

>* js 文件解读

通过在每个 js 文件中搜索`jandan_load_img`，最后可以在一个地址类似于`http://cdn.jandan.net/static/min/1d694f08895d377af4835a24f06090d0.29100001.js`的文件中找到这个函数的定义，将压缩的 JS 代码格式化查看，可以看到具体的定义如下片段：
```
function jandan_load_img(b) {
    var d = $(b);
    var f = d.next("span.img-hash");
    var e = f.text();
    f.remove();
    var c = f_Qa8je29JONvWCrmeT1AJocgAtaiNWkcN(e, "agC37Is2vpAYzkFI9WVObFDN5bcFn1Px");
```
这段代码的意思很容易看懂，首先它提取了当前标签下 css 为`img-hash`的 span 标签的文本,也就是我们最开始说的图片的 hash 值，然后把这个值和一个字符串参数（每个页面的这个参数是变动的，这个页面是 `agC37Is2vpAYzkFI9WVObFDN5bcFn1Px`）一起传递到另外一个函数`f_Qa8je29JONvWCrmeT1AJocgAtaiNWkcN`中，所以我们还要去查看这个函数的意义才行，这个函数就是用来生成图片链接的函数了。

>* f_ 函数的解读

可以在 js 中查找这个 f_ 函数的定义，可以看到有两个，但是没关系，根据代码从上到下执行的规律，我们只需要看比较靠后的那个就行了，完整的内容如下：
```
var f_Qa8je29JONvWCrmeT1AJocgAtaiNWkcN = function(m, r, d) {
    var e = "DECODE";
    var r = r ? r : "";
    var d = d ? d : 0;
    var q = 4;
    r = md5(r);
    var o = md5(r.substr(0, 16));
    var n = md5(r.substr(16, 16));
    if (q) { if (e == "DECODE") { var l = m.substr(0, q) } } else { var l = "" }
    var c = o + md5(o + l);
    var k;
    if (e == "DECODE") {
        m = m.substr(q);
        k = base64_decode(m)
    }
    var h = new Array(256);
    for (var g = 0; g < 256; g++) { h[g] = g }
    var b = new Array();
    for (var g = 0; g < 256; g++) { b[g] = c.charCodeAt(g % c.length) }
    for (var f = g = 0; g < 256; g++) {
        f = (f + h[g] + b[g]) % 256;
        tmp = h[g];
        h[g] = h[f];
        h[f] = tmp
    }
    var t = "";
    k = k.split("");
    for (var p = f = g = 0; g < k.length; g++) {
        p = (p + 1) % 256;
        f = (f + h[p]) % 256;
        tmp = h[p];
        h[p] = h[f];
        h[f] = tmp;
        t += chr(ord(k[g]) ^ (h[(h[p] + h[f]) % 256]))
    }
    if (e == "DECODE") { if ((t.substr(0, 10) == 0 || t.substr(0, 10) - time() > 0) && t.substr(10, 16) == md5(t.substr(26) + n).substr(0, 16)) { t = t.substr(26) } else { t = "" } }
    return t
};
```
这个函数需要传递3个参数，第一个参数是图片的 hash 值，第二个参数就是在`jandan_load_img`函数中看到的一个字符串，第三个参数其实没用，因为在`jandan_load_img`函数中根本没有传入。我们只需要按照 JS 代码的意思把这个函数改写成 Python 代码就行了。

>* Python改写函数

使用Python将f_函数改写之后应该是这样的：
```
def get_imgurl(m, r='', d=0):
    '''解密获取图片链接'''
    e = "DECODE"
    q = 4
    r = _md5(r)
    o = _md5(r[0:0 + 16])
    n = _md5(r[16:16 + 16])
    l = m[0:q]
    c = o + _md5(o + l)
    m = m[q:]
    k = _base64_decode(m)
    h = list(range(256))
    b = [ord(c[g % len(c)]) for g in range(256)]

    f = 0
    for g in range(0, 256):
        f = (f + h[g] + b[g]) % 256
        tmp = h[g]
        h[g] = h[f]
        h[f] = tmp

    t = ""
    p, f = 0, 0
    for g in range(0, len(k)):
        p = (p + 1) % 256
        f = (f + h[p]) % 256
        tmp = h[p]
        h[p] = h[f]
        h[f] = tmp
        t += chr(k[g] ^ (h[(h[p] + h[f]) % 256]))
    t = t[26:]
    return t
```
这个函数需要用到另外两个函数，第一个是 MD5 加密的函数，这个函数对应的是 JS 中这样的段落：
```
var o = md5(r.substr(0, 16));
```
js 的substr()函数其实就是 Python 里面的切片的用法，稍微查看一下定义就能懂，不解释。

MD5 加密转化成 Python 版本如下：
```
def _md5(value):
    '''md5加密'''
    m = hashlib.md5()
    m.update(value.encode('utf-8'))
    return m.hexdigest()
```
然后还有一个 bash64 的解码函数，这个函数在 js 中的这一个段用到了：
```
k = base64_decode(m)
```
使用 Python 的时候需要注意，如果直接使用 Python 的base64.b64decode的话会报错，具体的报错内容是：
```
binascii.Error: Incorrect padding
```
所以在将数据进行解码之前先要处理一下，具体的函数是：
```
def _base64_decode(data):
    '''bash64解码，要注意原字符串长度报错问题'''
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += '=' * missing_padding
    return base64.b64decode(data)
```
到这里，获取图片链接的函数就完成了，主要就是使用3个函数。

我们可以传入两个从网页中复制到的参数到这个函数中测试一下：
```
m = 'ece8ozWUT/VGGxW1hlbITPgE0XMZ9Y/yWpCi5Rz5F/h2uSWgxwV6IQl6DAeuFiT9mH2ep3CETLlpwyD+kU0YHpsHPLnY6LMHyIQo6sTu9/UdY5k+Vjt3EQ'
r = 'HpRB2OSft5RhlSyZaXV8xYpvEAgDThcA'
print(get_imgurl(m,r))
```
可以看到如下输出：
```
//ww3.sinaimg.cn/mw600/0073ob6Pgy1fpet9wku7dj30hs0qljuz.jpg
```
注意：这里的r参数是从每个页面中的 js 中复制的，每个页面的 js 地址是变动的，这个参数也是变动的。


## 获取 hash 和 js 地址

之前说过，hash 值是获取图片地址的关键参数，而另外的参数在 js 文件中，并且这个 js 文件每个页面不同，所以现在来提取这两个关键参数。

>* 批量获取 hash

获取图片的 hash 值很方便，我们可以使用 BeautifulSoup 的方法即可，具体的代码片段：
```
def get_urls(url):
    '''获取一个页面的所有图片的链接'''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'Host': 'jandan.net'
    }
    html = requests.get(url, headers=headers).text
    js_url = 'http:' + re.findall('<script src="(//cdn.jandan.net/static/min/[\w\d]+\.\d+\.js)"></script>', html)[-1]
    _r = get_r(js_url)
    soup = BeautifulSoup(html, 'lxml')
    tags = soup.select('.img-hash')
    for tag in tags:
        img_hash = tag.text
        img_url = get_imgurl(img_hash,_r)
        print(img_url)
```
提取图片 hash 的代码是这一句：
```
soup = BeautifulSoup(html, 'lxml')
    tags = soup.select('.img-hash')
    for tag in tags:
        img_hash = tag.text
```

>* 获取 js 中关键字符串

而获取 js 地址的方式是使用的正则表达式:
```
js_url = 'http:' + re.findall('<script src="(//cdn.jandan.net/static/min/[\w\d]+\.\d+\.js)"></script>', html)[-1]
```
这里要注意，因为正则提取的是一个列表，所以最后需要取列表中的一个链接，经过查看，我发现有的页面有两个这种 JS 文件，有一个是被注释掉了，所以都要使用最后一个，这个的表达方式是列表索引中使用[-1]取最后一个。

得到 js 地址之后需要请求，然后找到关键字符串，具体可以写成一个函数：
```
def get_r(js_url):
    '''获取关键字符串'''
    js = requests.get(js_url).text
    # 之前是使用下面注释的这个，后来煎蛋改了这个函数的名称
    # _r = re.findall('c=f_[\w\d]+\(e,"(.*?)"\)', js)[0]
    _r = re.findall('c=[\w\d]+\(e,"(.*?)"\)', js)[0]
    return _r
```

## 完整代码

下面就是获取一个页面的全部的图片链接的完整代码：
```
# -*- coding: utf-8 -*-
import requests
from bs4 import BeautifulSoup
import hashlib
import re
import base64


def _md5(value):
    '''md5加密'''
    m = hashlib.md5()
    m.update(value.encode('utf-8'))
    return m.hexdigest()


def _base64_decode(data):
    '''bash64解码，要注意原字符串长度报错问题'''
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += '=' * missing_padding
    return base64.b64decode(data)


def get_imgurl(m, r='', d=0):
    '''解密获取图片链接'''
    e = "DECODE"
    q = 4
    r = _md5(r)
    o = _md5(r[0:0 + 16])
    n = _md5(r[16:16 + 16])
    l = m[0:q]
    c = o + _md5(o + l)
    m = m[q:]
    k = _base64_decode(m)
    h = list(range(256))
    b = [ord(c[g % len(c)]) for g in range(256)]

    f = 0
    for g in range(0, 256):
        f = (f + h[g] + b[g]) % 256
        tmp = h[g]
        h[g] = h[f]
        h[f] = tmp

    t = ""
    p, f = 0, 0
    for g in range(0, len(k)):
        p = (p + 1) % 256
        f = (f + h[p]) % 256
        tmp = h[p]
        h[p] = h[f]
        h[f] = tmp
        t += chr(k[g] ^ (h[(h[p] + h[f]) % 256]))
    t = t[26:]
    return t


def get_r(js_url):
    '''获取关键字符串'''
    js = requests.get(js_url).text
    _r = re.findall('c=[\w\d]+\(e,"(.*?)"\)', js)[0]
    return _r


def get_urls(url):
    '''获取一个页面的所有图片的链接'''
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36',
        'Host': 'jandan.net'
    }
    html = requests.get(url, headers=headers).text
    js_url = 'http:' + re.findall('<script src="(//cdn.jandan.net/static/min/[\w\d]+\.\d+\.js)"></script>', html)[-1]
    _r = get_r(js_url)
    soup = BeautifulSoup(html, 'lxml')
    tags = soup.select('.img-hash')
    for tag in tags:
        img_hash = tag.text
        img_url = get_imgurl(img_hash,_r)
        print(img_url)


if __name__ == '__main__':
    get_urls('http://jandan.net/ooxx/page-44')
```

运行上面的代码，可以打印出这个页面的所有图片链接，部分链接如下：

```
//ww3.sinaimg.cn/mw600/0073ob6Pgy1fpet9wku7dj30hs0qljuz.jpg
//ww3.sinaimg.cn/mw600/0073tLPGgy1fpet9mszjwj30hs0g1jsv.jpg
//ww3.sinaimg.cn/mw600/0073ob6Pgy1fpesskkgobj31jk1jkk5b.jpg
//wx3.sinaimg.cn/mw600/006XfbArly1fpesq2jn1vj30j60svaz3.jpg
//wx3.sinaimg.cn/mw600/6967abd2gy1fpenoyobrcj20u03d0b2d.jpg
//wx3.sinaimg.cn/mw600/6967abd2gy1fpenp38v9uj20u03zkhdy.jpg
```

总结：到这里为止，提取煎蛋网妹子图的图片链接的方式其实已经给出来了，下面就是通过多线程+多进程的方式下载图片。



# [Python 爬虫]煎蛋网妹子图爬虫——多线程+多进程下载图片

> 上面文章全面解析了煎蛋网的妹子图的图片链接解密的方式，已经可以通过 Python 爬虫代码批量获取每个页面中的图片地址。但是上一篇文章中并没有写图片下载的函数，这一篇文章就来使用 Python 的多线程和多进程来批量下载图片。

## 多线程下载

>* 多线程源代码
```
def load_imgs(url,file):
    '''多线程下载单页的所有图片'''
    threads = []
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Host': 'jandan.net'
    }
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, 'lxml')
    # 这个地方必须使用[-1]来提取js地址，因为有的页面有两个js地址，其中第一个是被注释了不用的
    js_url = re.findall('<script src="(//cdn.jandan.net/static/min/[\w\d]+\.\d+\.js)"></script>', html)[-1]
    _r = get_r('http:{}'.format(js_url))
    tags = soup.select('.img-hash')
    for each in tags:
        hash = each.text
        img_url = 'http:' + get_imgurl(hash, _r)
        t = threading.Thread(target=load_img,args=(img_url,file))
        threads.append(t)
    for i in threads:
        i.start()
    for i in threads:
        i.join()
    print(url,'is ok')
```

>* 多线程代码解读

* 这是一个爬虫类（上一篇中提到的，本文末尾也会给出完整代码）的函数，这个函数需要传递2个参数，第一个参数是一个地址，也就是需要下载图片的网页，第二个参数是一个本地文件夹的地址，也就是图片下载之后保存的文件夹。
* 思路很简单，就是先请求当前页，然后先调用第一篇文章中的函数去获取图片的 hash 值和 js 中的关键字符串参数，然后再调用图片链接解密函数，得到图片的真实地址，最后调用一个图片下载函数 load_img 使用多线程下载图片。
* 下载图片的函数如下：
```
def load_img(imgurl, file):
    '''下载单张图片到制定的文件夹下'''
    name = imgurl.split('/')[-1]
    file = "{}\\{}".format(file,name)
    item = requests.get(imgurl).content
    with open(file,'wb') as f:
        f.write(item)
    print('{} is loaded'.format(name))
```
这个函数就很简单了，就是传入一个图片的地址和需要保存图片的文件地址，然后写入图片就行了，不多说。

* 多线程的实现：

这里是使用的 Python 内置的多线程方式，首先创建一个放线程的列表：
```
threads = []
```

然后将当前页面中的每个图片链接最为参数传入到线程中，而线程中的第一个函数参数就是上面提到的下载图片的函数了，具体代码是这一段：
```
t = threading.Thread(target=load_img,args=(img_url,file))
threads.append(t)
```

最后运行多线程即可：
```
for i in threads:
    i.start()
for i in threads:
    i.join()
```
以上代码就是实现的单个页面的多线程下载图片的方式，因为下载图片是一个IO密集型的操作，所以使用多线程可以有效的提高图片下载的效率，更重要的是图片下载是互相不影响的，所以也不需要去设置线程锁，这算是很简单的多线程操作了。

## 多进程下载

上面的的多线程下载实现了单个页面的图片使用多线程去下载，如果我们要实现同时去请求多个页面呢？当然，一样可以使用多线程，首先多线程请求多个页面，然后多线程下载多个图片，也就是多线程中嵌套多线程的做法。不过为了展示 Python 多进程的用法，这里实现的是使用多进程中嵌套多线程的方法。

>* 多进程代码展示
```
def main(start,end,file):
    '''多进程下载多页的图片,传入参数是开始页码数，结束页码，图片保存文件夹地址'''
    pool = multiprocessing.Pool(processes=4)
    base_url = 'http://jandan.net/ooxx/page-{}'
    for i in range(start,end+1):
        url = base_url.format(i)
        pool.apply_async(func=load_imgs,args=(url,file))
    pool.close()
    pool.join()
```

>* 多进程代码解读

* 上面这个函数是整个爬虫类最终要运行的函数，它需要3个参数，前面两个参数是需要爬取的页面的起始页码和终止页码，第3个参数同样是图片保存的文件夹地址。
* 首先创建一个进程池：
```
pool = multiprocessing.Pool(processes=4)
```
当然，整个进程池我设置了4个进行，这个进程数的数量可以自己去设定。

* 循环创建下载链接，然后加入到进程池中：
```
for i in range(start,end+1):
    url = base_url.format(i)
    pool.apply_async(func=load_imgs,args=(url,file))
```

这个操作其实跟多线程的使用非常相识，同样是给进程池的函数传递2个参数，第一个参数就是之前用来多线程下载单页图片的下载函数，第二个参数就是需要传递给下载函数的参数，也就是链接和文件夹地址。

* 运行多进程：
```
pool.close()
pool.join()
```

多进程添加完毕就可以运行起来了，最后可以查看运行的效果，打印一下消耗的时间，可以去跟单进程单线程对比，应该会快很多。

```
if __name__ == '__main__':
    import time
    t = time.time()
    main(23,25,r'C:\Users\XXOO\Desktop\meizi')
    print(time.time()-t)
```
运行部分效果如下：
```
46401622gy1fp9obr1iwzj20hs0hs408.jpg is loaded
0073ob6Pgy1fpa9qda270g304s06m4qp.gif is loaded
0073ob6Pgy1fpam2nkjrmg308r08me84.gif is loaded
http://jandan.net/ooxx/page-25 is ok
0073ob6Pgy1fp9ptkxfirg308w06oe83.gif is loaded
http://jandan.net/ooxx/page-23 is ok
006GJYM5gy1fp9vomnhvvg30dc0goqv9.gif is loaded
46401622gy1fpab28pdkcg20g70k8he1.gif is loaded
46401622gy1fpabhbyq2vg20g70k84qx.gif is loaded
http://jandan.net/ooxx/page-24 is ok
74.57059788703918
```

## 完整代码

从第一篇到第二篇的完整代码如下，只需要修改最后运行的函数中页码的起始页码数和自己想要保存的文件夹地址，就可以运行爬虫程序了。
```
# -*- coding: utf-8 -*-
import hashlib
import base64
import requests
from bs4 import BeautifulSoup
import re
import threading
import multiprocessing


def _md5(value):
    '''md5加密'''
    m = hashlib.md5()
    m.update(value.encode('utf-8'))
    return m.hexdigest()


def _base64_decode(data):
    '''bash64解码，要注意原字符串长度报错问题'''
    missing_padding = 4 - len(data) % 4
    if missing_padding:
        data += '=' * missing_padding
    return base64.b64decode(data)


def get_imgurl(m, r='', d=0):
    '''解密获取图片链接'''
    e = "DECODE"
    q = 4
    r = _md5(r)
    o = _md5(r[0:0 + 16])
    n = _md5(r[16:16 + 16])
    l = m[0:q]
    c = o + _md5(o + l)
    m = m[q:]
    k = _base64_decode(m)
    h = list(range(256))
    b = [ord(c[g % len(c)]) for g in range(256)]

    f = 0
    for g in range(0, 256):
        f = (f + h[g] + b[g]) % 256
        tmp = h[g]
        h[g] = h[f]
        h[f] = tmp

    t = ""
    p, f = 0, 0
    for g in range(0, len(k)):
        p = (p + 1) % 256
        f = (f + h[p]) % 256
        tmp = h[p]
        h[p] = h[f]
        h[f] = tmp
        t += chr(k[g] ^ (h[(h[p] + h[f]) % 256]))
    t = t[26:]
    return t


def get_r(js_url):
    '''获取关键字符串'''
    js = requests.get(js_url).text
    # 之前用的下面注释掉的这个，后来煎蛋改了函数名称，少个f_
    # _r = re.findall('c=f_[\w\d]+\(e,"(.*?)"\)', js)[0]
    _r = re.findall('c=[\w\d]+\(e,"(.*?)"\)', js)[0]
    return _r


def load_img(imgurl, file):
    '''下载单张图片到制定的文件夹下'''
    name = imgurl.split('/')[-1]
    file = "{}\\{}".format(file,name)
    item = requests.get(imgurl).content
    with open(file,'wb') as f:
        f.write(item)
    print('{} is loaded'.format(name))



def load_imgs(url,file):
    '''多线程下载单页的所有图片'''
    threads = []
    headers = {
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.8; rv:49.0) Gecko/20100101 Firefox/49.0',
        'Host': 'jandan.net'
    }
    html = requests.get(url, headers=headers).text
    soup = BeautifulSoup(html, 'lxml')
    # 这个地方必须使用[-1]来提取js地址，因为有的页面有两个js地址，其中第一个是被注释了不用的
    js_url = re.findall('<script src="(//cdn.jandan.net/static/min/[\w\d]+\.\d+\.js)"></script>', html)[-1]
    _r = get_r('http:{}'.format(js_url))
    tags = soup.select('.img-hash')
    for each in tags:
        hash = each.text
        img_url = 'http:' + get_imgurl(hash, _r)
        t = threading.Thread(target=load_img,args=(img_url,file))
        threads.append(t)
    for i in threads:
        i.start()
    for i in threads:
        i.join()
    print(url,'is ok')

def main(start,end,file):
    '''多进程下载多页的图片,传入参数是开始页码数，结束页码，图片保存文件夹地址'''
    pool = multiprocessing.Pool(processes=4)
    base_url = 'http://jandan.net/ooxx/page-{}'
    for i in range(start,end+1):
        url = base_url.format(i)
        pool.apply_async(func=load_imgs,args=(url,file))
    pool.close()
    pool.join()


if __name__ == '__main__':
    import time
    t = time.time()
    main(23,25,r'C:\Users\XXOO\Desktop\meizi')
    print(time.time()-t)
```

总结：以上就是使用多进程+多线程下载煎蛋网妹子图的所有代码，我在代码中没有设置延时时间，因为想要测试爬虫的效率，毕竟我也就爬了3页。当然，希望看到这篇文章的人如果要大量爬图片的话，尽量设置足够的 sleep 时间来延时爬取，这样既可以避免自己的 IP 被封，也不至于给煎蛋的服务器带来压力。
