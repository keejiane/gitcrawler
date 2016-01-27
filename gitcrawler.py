#coding=utf-8
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import time
import re
import urllib
import urllib2
import argparse
from bs4 import BeautifulSoup

def getPage(pageNum):
	try:
		url = 'https://github.com/search?p=' + str(pageNum) + '&q=' + str(args.name) + '%2Cpassword&ref=searchresults&type=Code&utf8=%E2%9C%93'
		user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/46.0.2490.71 Safari/537.36'
		headers = {'User_agent' : user_agent}
		request = urllib2.Request(url , headers = headers)
		respond = urllib2.urlopen(request)
		content = respond.read().decode('utf-8')
		return content
	except urllib2.URLError, e:
		if hasattr(e , "code"):
			print e.code
		if hasattr(e , "reason"):
			print e.reason

def getPageNum(page):
	soup = BeautifulSoup(page , "lxml")
	pageNum = soup.find(class_ = "next_page").previous_element.previous_element
	#print pageNum
	if pageNum:
		return pageNum.strip()
	else:
		return None

def getResultNum(page):
	soup = BeautifulSoup(page , "lxml")
	resultNum = soup.find(class_ = "counter").string
	if resultNum:
		return resultNum.strip()
	else:
		return None

def isBothExist(word1, word2, cnt):
	#flag = False
	if word1 in cnt:
		if word2 in cnt:
			flag = True
			#print 'Two keywords are both exist!'
		else:
			flag = False
			#print "only %s" %word1
	elif word2 not in cnt:
		flag = False
		#print "None of them exists."
	else:
		flag = False
		#print "only %s" %word2
	#print flag
	return flag

def codeFilter(code):
	#flag = False
	#soup = BeautifulSoup(page, "lxml")
	#table = soup.find(class_ = "highlight").get_text()
	afterPwd = []
	#判断code中是否同时含有参数name及‘password’关键词
	if isBothExist(str(args.name), 'password', code):
	#判断password字符串后面是否存在密码
		for i in re.finditer('password', code):
			for j in code[i.start() + 8:i.start() + 11]:
				afterPwd.append(str(j))
			#print afterPwd
			if ':' in afterPwd or '=' in afterPwd:
				flag2 = True
			else:
				flag2 = False
	else:
		flag2 = False
	#print flag2
	return flag2

		
def getItems(page):
	soup = BeautifulSoup(page , "lxml")
	searchResults = soup.find_all(class_ = "code-list-item code-list-item-public ")
#	items = itemsPerPage = []
	for result in searchResults:
		acount = result.find('img').attrs['alt']
		project = result.find('p').contents[1].string
		filename = result.find('p').contents[3].string
		fileurl = result.find('p').contents[3].attrs['href']
		"""自动过滤不准确的搜索结果"""
		codeText = result.get_text()
		if codeFilter(codeText):
			print '\nGET IT!!!\nThere is a password exposed probably!'
			print u"用户%s在github上创建的项目%s中，文件%s存在敏感信息。" %(acount, project, filename)
			print u"文件链接为：https://github.com%s\n" %fileurl
		else:
			print 'I found nothing!'

def getAll():
	indexPage = getPage(1)
	pageNum = getPageNum(indexPage)
	resultNum = getResultNum(indexPage)
	#print pageNum
	print u"查找到结果共" + str(pageNum) + "页。"
	for i in range(1, int(pageNum)+1):
		'''int(pageNum)+1):'''
		print u"正在写入第" + str(i) + "页数据..."
		page = getPage(i)
		getItems(page)
		time.sleep(3)
	print u"读取结束，共写入" + str(resultNum) + "条数据。"

parser = argparse.ArgumentParser()
parser.add_argument("name", help="the name you want to search in github. eg:baidu")
args = parser.parse_args()
getAll()

		

