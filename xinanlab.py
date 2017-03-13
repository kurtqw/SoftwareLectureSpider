# coding:utf-8
import Queue
import re
import requests
import string
import urllib2
import sys  
from urllib2 import Request, urlopen, URLError, HTTPError
from lxml import html,etree
from bs4 import BeautifulSoup
import MySQLdb


#解决ascii编码问题
reload(sys)  
sys.setdefaultencoding('utf-8') 

#设置主页
initial_page = "http://sklois.iie.cas.cn/tzgg/tzgg_16520/"
#改变超链接筛选规则
rules = '//a[@class = "hh14" or @class = "bai12_22h"]/@href'

def downloading(initial_page,rules):
    #获取第一个页面
    r = requests.get(initial_page)
    data = r.text

    #初始化队列和已访问集合
    url_queue = Queue.Queue()
    seen = set()
    seen.add(initial_page)
    url_queue.put(initial_page)

    i=0
    while(True): 
        if url_queue.qsize()>0:
            #爬入下一个网页
            current_url = url_queue.get()
            print current_url
            #限制爬虫活动范围
            pattern = re.compile(initial_page)
            match = pattern.search(current_url)
                   
            #get网页的源代码
            r = requests.get(current_url)
            data = r.text

            #自动填充成五位的文件名
            sName = string.zfill(i,5) + '.html'      
            #print 'Downloading no.' + str(i) + ' page and saving as ' + sName + '......'  

            #下载当前网页
            f = open(sName,'w+')  
            try:
                m = urllib2.urlopen(current_url).read()
            except URLError, e:    
                if hasattr(e, 'reason'):    
                    print 'We failed to reach a server.'    
                    print 'Reason: ', e.reason    
                elif hasattr(e, 'code'):    
                    print 'The server couldn\'t fulfill the request.'    
                    print 'Error code: ', e.code  
            
            f.write(m)  
            f.close() 
               

            #在下载下来的网页中读取所需信息
            file1 = open (string.zfill(i,5) + '.html')
            text = file1.read()
            pattern1 =re.compile(r'学术报告' or r'讲座')
            if re.search(pattern1,text):
                
                #去除html标记 
                text = re.sub(r'<(S*?)[^>]*>.*?|<.*?/?','',text)
                text = re.sub(r'&nbsp;','',text)
                get=0
                insertlist =  ['','','','','','','',0,0]
                textlist = re.findall(r"(?<=题目：).*?(?=\n)|(?<=Title:).*?(?=\n)|(?<=题目:).*?(?=\n)|(?<=目：).*?(?=\n)" ,text)
                if len(textlist)>0:
                    insertlist[0]=textlist[0]
                    get=1
                textlist = re.findall(r"(?<=报告人：).*?(?=\n)|(?<=Speaker:).*?(?=\n)|(?<=报告人:).*?(?=\n)",text)
                if len(textlist)>0:
                    insertlist[1]=textlist[0]
                    get=1
                textlist = re.findall(r"(?<=时间：).*?(?=\n)|(?<=Time:).*?(?=\n)|(?<=时间:).*?(?=\n)|(?<=日期:).*?(?=\n)|(?<=间：).*?(?=\n)",text)
                if len(textlist)>0:
                    insertlist[2]=textlist[0]
                    syear=re.findall(r"\d*(?=年)",textlist[0])
                    smonth=re.findall(r"\d*(?=月)",textlist[0])
                    sday=re.findall(r"\d*(?=日)",textlist[0])
                    pattern2 = re.compile(r'年')
                    if re.search(pattern2,textlist[0]):
                        stime=syear[0]+string.zfill(smonth[0],2)+string.zfill(sday[0],2)
                        insertlist[7]=int(stime)
                    get=1
                textlist = re.findall(r"(?<=地点：).*?(?=\n)|(?<=Address:).*?(?=\n)|(?<=地点:).*?(?=\n)|(?<=点：).*?(?=\n)|(?<=Place:).*?(?=\n)",text)
                if len(textlist)>0:
                    insertlist[4]=textlist[0]
                    get=1
                if get==1:
                    insertlist[6]=current_url
                    insertlist[8]=insertlist[7]
            
                    insertlist[5]='信息安全国家实验室'

                    try:
                        conn=MySQLdb.connect(host='localhost',user='root',passwd='805469',db='test',charset='utf8',port=3307)
                        cur=conn.cursor()
                         
                        '''cur.execute('create database if not exists test')
                        conn.select_db('test')
                        cur.execute('create table cs(id int,info varchar(20))')'''
                         
                        cur.execute('insert into cs values(%s,%s,%s,%s,%s,%s,%s,%s,%s)',insertlist)
                     
                        conn.commit()
                        cur.close()
                        conn.close()
                     
                    except MySQLdb.Error,e:
                         print "Mysql Error %d: %s" % (e.args[0], e.args[1])

            file1.close()

            i+=1

            #用树结构储存网页
            tree = html.fromstring(data)
            link_list = tree.xpath(rules)
           

            #补全网页地址      #link_list = re.findall(r"(?<=href=\").+?(?=\")|(?<=href=\').+?(?=\')" ,data)
            link_list = map(lambda i: 'http' + '://' + i if i[0] == '/' else initial_page + i if i[0] == '#' else initial_page + i if i[0]<>'h' else i, link_list)


            #记录下当前网页中所有符合的超链接
            f = open('superlink.txt','w+')  
            for url in link_list:
                f.write(url+'\n') 
            f.close() 

            #把超链接放入队列
            for next_url in link_list:
                if next_url not in seen:      
                    seen.add(next_url)
                    url_queue.put(next_url)
        else:
            break

downloading(initial_page,rules)
