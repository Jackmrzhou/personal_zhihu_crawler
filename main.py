import requests
import json
from bs4 import BeautifulSoup
import threading
import time

def get_cookie():
	with open('cookies.json', 'r') as fp:
		cookies_json = fp.read()
	my_cookies = requests.utils.cookiejar_from_dict(json.loads(cookies_json))
	return my_cookies

def get_xsrf_from_cookies(my_cookies):
	return my_cookies['_xsrf']

def get_zhihu_html_object(abs_url, cookies):
	'''
		net IO
	'''
	headers = {
		'User-Agent':'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'
	}
	zhihu_html_object = requests.get(abs_url, headers = headers, cookies = cookies)
	return zhihu_html_object

def parse_html(lock, abs_url, zhihu_html_object = None, feed_html = None):

	if zhihu_html_object:
		soup = BeautifulSoup(zhihu_html_object.text, 'lxml')
	else:
		soup = BeautifulSoup(feed_html, 'lxml')
	item_list = soup.find_all('div', attrs={'class' : 'feed-main'})
	
	def parse_tag(item):
		'''
			get source, title, name, summary, link
		'''
		try:
			source = item.find('div', attrs = {'class' : 'feed-source'}).text
		except:
			source = '无来源。\n'
		item_content = item.find('div', attrs = {'class' : 'feed-content'})
		try:
			title = item_content.h2.a.text
		except:
			title = '无标题.\n'

		try:
			name = item_content.find(
				'div',
				attrs = {'class':'zm-item-rich-text expandable js-collapse-body'}
				).get('data-author-name') + '\n'
		except:
			try:
				name = item_content.find('div', attrs = {'class':'post-content'}).get('data-author-name') +'\n'
			except:
				name = '不是回答，没有名字。\n'

		try:
			summary = item_content.find('div',attrs = {'class':'zh-summary summary clearfix'}).text
		except:
			summary = 'NO SUMMARY!\n'
		
		try:
			link = item_content.find('div',attrs = {'class':'zh-summary summary clearfix'}).a.get('href') +'\n'	
		except:
			try:
				link = item_content.h2.a.get('href') + '\n'
			except:
				link = 'no link'
		if link[0:4] != 'http' and link != 'no link':
			link = abs_url + link

		'''		
		with open('zhihu.txt', 'a', encoding='utf8') as fp:
			fp.write(source)
			fp.write('标题：  ' + title)
			fp.write('姓名：  ' + name)
			fp.write('概述：  ' + summary)
			fp.write(link)
			fp.write('#' * 40)
			fp.write('\n')
		#这样写频繁重新open会浪费性能
		'''
		global fp
		lock.acquire()
		fp.write(source)
		fp.write('标题：  ' + title)
		fp.write('姓名：  ' + name)
		fp.write('概述：  ' + summary)
		fp.write(link)
		fp.write('#' * 40 +'\n')
		lock.release()

	for item in item_list:
		parse_tag(item)		

'''
	ts = []
	for item in item_list:
		t = threading.Thread(target = parse_tag(item))
		ts.append(t)
		t.start()

	for t in ts:
		t.join()
'''
	

def get_parse_AJAX_html(lock, AJAX_url, _xsrf, cookies, offset, start):
	headers ={
		'Accept':'*/*',
		'Accept-Encoding':'gzip, deflate, br',
		'Connection':'keep-alive',
		'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
		'User-Agent':'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36',
		'Referer':'https://www.zhihu.com/',
		'X-Requested-With':'XMLHttpRequest',
		'X-Xsrftoken':_xsrf
	}
	data = {
		'params':'{"offset": %d,"start":%s}' %(offset, str(start)),
		'method':'next'
	}
	json_data = requests.post(AJAX_url,
		headers = headers,
		cookies = cookies,
		data = data).json()
	if json_data['r'] != 0:
		print('读取失败！')
	else:
		feed_back = json_data['msg']
	
	for feed_html in feed_back:
		parse_html(lock = lock, feed_html = feed_html, abs_url = abs_url)

'''
class item(object):

	def __init__(self, title, name, summary, link):
		self.title = title
		self.name = name
		self.summary = summary
		self.link = link

	def __repr__(self):
		return '<This is a dymanic>'
#本来想用类，后来一想没有必要
'''

if __name__ == '__main__':

	abs_url = 'https://www.zhihu.com'
	AJAX_url = 'https://www.zhihu.com/node/TopStory2FeedList'
	fp = open('zhihu.txt', 'a', encoding='utf8')
	lock = threading.Lock()
	pages = int(input('Pages:'))
	
	total_time = 0
	before = time.time()
	
	my_cookies = get_cookie()
	_xsrf = get_xsrf_from_cookies(my_cookies)
	ts = []
	
	def previous():
		
		zhihu_html_object = get_zhihu_html_object(abs_url, my_cookies)
		parse_html(lock, abs_url, zhihu_html_object = zhihu_html_object)

	t = threading.Thread(target = previous)
	t.start()
	ts.append(t)
	
	for i in range(pages):
#		get_parse_AJAX_html(AJAX_url, _xsrf, my_cookies, 10, (i+1) * 10 - 1)
#改前的代码
#		t = threading.Thread(target = get_parse_AJAX_html(AJAX_url, _xsrf, my_cookies, 10, (i+1) * 10 - 1))
#		t.start()
#错误写法，参数不能这样传，否则无法实现多线程
		t = threading.Thread(
			target = get_parse_AJAX_html,
			args = [lock, AJAX_url, _xsrf, my_cookies,10,(i+1) * 10 - 1]
			)
		t.start()
		ts.append(t)

	for t in ts:
		t.join()

	fp.close()
	after = time.time()
	total_time += after - before

	print('Done.')
	print('Time consumed:%s' %total_time)