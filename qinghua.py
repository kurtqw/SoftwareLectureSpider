# -*- coding: utf-8 -*-
#清华
import Queue
import re
import requests
import string
import urllib2
import sys  
from urllib2 import Request, urlopen, URLError, HTTPError
from lxml import html,etree
from bs4 import BeautifulSoup
import json
import MySQLdb

#解决ascii编码问题
reload(sys)  
sys.setdefaultencoding('utf-8')

page = requests.get('http://iiis.tsinghua.edu.cn/seminars/')
text=page.text.decode('utf-8').encode('utf-8')
tree1 = html.fromstring(text)
hrefs = tree1.xpath('//tr/td/a/@href')
hrefs = map(lambda i1: 'http://iiis.tsinghua.edu.cn' + i1 if i1[0] == '/' else  i1, hrefs)
titles = tree1.xpath('//tr/td[1]/a/text()')
#speakers = tree1.xpath('//tr/td[2]/text[not(self::br)]')
speakers = re.findall(r"(?<=\n\s{36}).*?(?=</a><br>)",text)
stime = tree1.xpath('//tr/td[3]/text()')

sdate=['','','','','','','','','','','','','','','','','','','','']
for i in range(0,19):
	syear=re.findall(r"\d{4}",stime[i])
	smonth=re.findall(r"(?<=\d{4}-)\d{2}",stime[i])
	sday=re.findall(r"(?<=\d{4}-\d{2}-)\d{2}",stime[i])
	sdate[i] = syear[0]+string.zfill(smonth[0],2)+string.zfill(sday[0],2)
	speakers[i] = re.sub(r'<(S*?)[^>]*>.*?|<.*?/?','',speakers[i])

addresses = tree1.xpath('//tr/td[4]/text()')

university = "清华大学"


for i in range(0,19):
	insertlist = [titles[i],speakers[i],stime[i],stime[i],addresses[i],university,hrefs[i],sdate[i],sdate[i]]
	try:
		conn=MySQLdb.connect(host='localhost',user='root',passwd='805469',db='test',charset='utf8',port=3307)
		cur=conn.cursor()
     
		cur.execute('insert into cs values(%s,%s,%s,%s,%s,%s,%s,%s,%s)',insertlist)
    
		conn.commit()
		cur.close()
		conn.close()
     
	except MySQLdb.Error,e:
		print "Mysql Error %d: %s" % (e.args[0], e.args[1])

'''print hrefs
print titles
print json.dumps(speakers,encoding="UTF-8",ensure_ascii=False)
print stime
print addresses'''

#string.strip()去处空格
#print json.dumps(dict,encoding="UTF-8",ensure_ascii=False)


j=2
while (j < 42 and j<>24 and j<>38 ):
	url = 'http://iiis.tsinghua.edu.cn/list-265-'+ str(j) +'.html'
	print url
	page = requests.get(url)
	text=page.text.decode('utf-8').encode('utf-8')
	tree1 = html.fromstring(text)
	hrefs = tree1.xpath('//tr/td/a/@href')
	hrefs = map(lambda i1: 'http://iiis.tsinghua.edu.cn' + i1 if i1[0] == '/' else  i1, hrefs)
	titles = tree1.xpath('//tr/td[1]/a/text()')
	#speakers = tree1.xpath('//tr/td[2]/text[not(self::br)]')
	speakers = re.findall(r"(?<=\n\s{36}).*?(?=</a><br>)",text)
	stime = tree1.xpath('//tr/td[3]/text()')
	sdate=['','','','','','','','','','','','','','','','','','','','']
	for i in range(0,19):
		#限制爬虫活动范围
		pattern = re.compile('http://iiis.tsinghua.edu.cn/')
		match = pattern.search(hrefs[i])
		if match == 0:
			hrefs[i]=''
		syear=re.findall(r"\d{4}",stime[i])
		smonth=re.findall(r"(?<=\d{4}-)\d{2}",stime[i])
		sday=re.findall(r"(?<=\d{4}-\d{2}-)\d{2}",stime[i])
		sdate[i] = syear[0]+string.zfill(smonth[0],2)+string.zfill(sday[0],2)
		speakers[i] = re.sub(r'<(S*?)[^>]*>.*?|<.*?/?','',speakers[i])
	addresses = tree1.xpath('//tr/td[4]/text()')

	university = "清华大学"


	for i in range(0,19):
		insertlist = [titles[i],speakers[i],stime[i],stime[i],addresses[i],university,hrefs[i],sdate[i],sdate[i]]
		try:
			conn=MySQLdb.connect(host='localhost',user='root',passwd='805469',db='test',charset='utf8',port=3307)
			cur=conn.cursor()
	     
			cur.execute('insert into cs values(%s,%s,%s,%s,%s,%s,%s,%s,%s)',insertlist)
	    
			conn.commit()
			cur.close()
			conn.close()
	     
		except MySQLdb.Error,e:
			print "Mysql Error %d: %s" % (e.args[0], e.args[1])
	'''print hrefs
	print titles
	print speakers
	print stime
	print addresses'''

	j+=1
	if j==24 or j==38:
		j+=1