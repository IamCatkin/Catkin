#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @Time    : 2018/1/25 16:44
# @Author  : Catkin
# @File    : youdao.py
import sys
import json
import http.client
import hashlib 
import urllib.request
import random

html = """
<html>
<head>
<meta charset="UTF-8">
<script type="text/javascript">function playSound(){var ky = document.getElementById("key");var word = ky.childNodes[0].nodeValue;var api = "http://dict.youdao.com/dictvoice?audio=" + encodeURIComponent(word);var ado = document.getElementById("media");try{ado.ended = true;ado.setAttribute("src",api);ado.load();ado.play();return false;}catch(err){alert(err.description);return false;}}</script>
</head>
<body>
<style type="text/css">
      div.block {
      border:1px solid #BEBEBE;
      background:#F0F0F0;
      margin-left:20px;
      border-radius: 5px;
      }
      div.name {
      margin-top:10px;
      margin-bottom:5px;
      margin-left:20px;
      font-size:13px;
      font-weight:bold;
      }
      div.item {
      padding:5px;
      font-size:12px;
      margin: 0px 10px 0px 10px;
      }
      #web {
      border-style: none none solid none;
      border-color: #BEBEBE;
      border-bottom-width: 1px;
      }
    </style>
    <div class="content">
      <div class="name"><i>查询:</i></div>
      <div class="block">
       %s
      </div>
      <div class="name"><i>有道翻译:</i></div>
      <div class="block">
    %s
      </div>
      <div class="name"><i>有道词典-基本词典:</i></div>
      <div class="block">
    %s
      </div>
      <div class="name"><i>有道词典-网络释义:</i></div>
      <div class="block">
       %s
      </div>
      <div class="name"><i>更多结果:</i></div>
      <div class="block">
       %s
      </div>
    </div>
</body>
</html>
"""

errorHtml = """
<html><body>
<div class="block">
<div class="item">%s</div>
</div>
</body></html>
"""

errorResult = {'0':'', '20':'要翻译的文本过长', '30':'无法进行有效的翻译',
              '40':'不支持的语言类型', '50':'无效的key'}

def printHtml(errorCode, query, translation, basic, web):
    """打印html"""
    if errorCode != "0":
        print(errorHtml % errorResult[errorCode])
        return
    item = '<div class="item">%s</div>'
    #有道翻译
    q = item % ('<b>"%s"</b>' % query)
    trans = ''
    for i in translation:
        trans += item % ('<b>"%s"</b>' % i)

    #有道词典
    key = ''
    if basic:
        key += '<span id="key" style="font-weight:bold">%s</span>' % (query + ' ')
        if 'phonetic' in basic.keys():
            key += '[%s]' % basic['phonetic']
            key += '<button id="sound" onclick="playSound()">sound</button><audio id="media"></audio>'
        key = item % key
        if 'explains' in basic.keys():
            #判断查询的词是不是中文
            isChinese = False
            for c in query:
                if ord(c) >= 0x4e00 and ord(c) <= 0x9fa5:
                    isChinese = True
                    break
            if not isChinese:
                for i in basic['explains']:
                    key += item % i
            else:
                for i in basic['explains']:
                    key += item % ('<a href="%s">%s</a>' % (i, i))
        key += item % ('<a href="http://dict.youdao.com/w/%s">%s</a>' % (query, '更多解释'))

    #web词典
    webdict = ''
    webitem = '<div %s class="item">%s<br/>%s</div>'
    if web:
        if len(web) > 1:
            for i in range(len(web)-1):
                webdict += webitem % ('id="web"', web[i]['key'], ', '.join(web[i]['value']))
        webdict += webitem % ('', web[-1]['key'], ', '.join(web[-1]['value']))

    if not key:
        key = item % '对不起,没有结果'
    if not webdict:
        webdict = item % '对不起,没有结果'
    #更多搜索
    moreSearch = '<div class="item"><a href="https://cn.bing.com/dict/search?q=' + \
      query + '">通过Bing词典搜索</a></div>'
    moreSearch += '<div class="item"><a href="http://www.iciba.com/' + \
      query + '">通过iciba词典搜索</a></div>'
    moreSearch += '<div class="item"><a href="http://www.baidu.com/s?wd=' + \
      query + '">通过百度搜索</a></div>'
    result = html % (q, trans, key, webdict, moreSearch)
    utf8stdout = open(1, 'w', encoding='utf-8', closefd=False) # fd 1 is stdout
    print(result, file=utf8stdout)

def getData(string):
    data = json.loads(string)
    errorCode = data['errorCode']
    query = data['query']
    translation = data['translation']
    basic = {}
    if 'basic' in data.keys():
        basic = data['basic']
    web = []
    if 'web' in data.keys():
        web = data['web']
    
    printHtml(errorCode, query, translation, basic, web)


#api信息
appKey = '你的应用ID'
secretKey = '你的密钥'

def searchWord(word):
    #加盐
    httpClient = None
    myurl = '/api'
    q = word
    fromLang = 'EN'
    toLang = 'zh-CHS'
    salt = random.randint(1, 65536)
    sign = appKey+q+str(salt)+secretKey
    m1 = hashlib.md5()
    m1.update(sign.encode('UTF-8'))
    sign = m1.hexdigest()
    myurl = myurl+'?appKey='+appKey+'&q='+urllib.request.quote(q)+'&from='+fromLang+'&to='+toLang+'&salt='+str(salt)+'&sign='+sign
    try:
        httpClient = http.client.HTTPConnection('openapi.youdao.com')
        httpClient.request('GET', myurl)
     
        #response是HTTPResponse对象
        response = httpClient.getresponse()
        k = response.read()
        getData(k)
    except Exception as e:
        print(e)
    finally:
        if httpClient:
            httpClient.close()
if __name__ == '__main__':
    searchWord(sys.argv[1])
