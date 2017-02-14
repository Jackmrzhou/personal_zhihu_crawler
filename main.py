import requests
import json
from bs4 import BeautifulSoup

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

def parse_html(abs_url, zhihu_html_object = None, feed_html = None):

	if zhihu_html_object:
		soup = BeautifulSoup(zhihu_html_object.text, 'lxml')
	else:
		soup = BeautifulSoup(feed_html, 'lxml')
	item_list = soup.find_all('div', attrs={'class' : 'feed-main'})
	for item in item_list:
		'''
			get source, title, name, summary, link
		'''
		source = item.find('div', attrs = {'class' : 'feed-source'}).text
		item_content = item.find('div', attrs = {'class' : 'feed-content'})
		try:
			title = item_content.h2.a.text
		except:
			title = '无标题'

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
			link = item_content.h2.a.get('href') + '\n'
		if link[0:4] != 'http':
			link = abs_url + link

		with open('zhihu.txt', 'a', encoding='utf8') as fp:
			fp.write(source)
			fp.write('标题：  ' + title)
			fp.write('姓名：  ' + name)
			fp.write('概述：  ' + summary)
			fp.write(link)
			fp.write('#' * 40)
			fp.write('\n')

def get_AJAX_html(AJAX_url, _xsrf, cookies, offset, start):
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
	return feed_back

def parse_feed_back(feed_back, abs_url):
	
	for feed_html in feed_back:
		parse_html(feed_html = feed_html, abs_url = abs_url)

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
	
	my_cookies = get_cookie()
	_xsrf = get_xsrf_from_cookies(my_cookies)
	zhihu_html_object = get_zhihu_html_object(abs_url, my_cookies)
	parse_html(abs_url, zhihu_html_object = zhihu_html_object)
	pages = int(input('Pages:'))
	for i in range(pages):
		feed_back = get_AJAX_html(AJAX_url, _xsrf, my_cookies, 10, (i+1) * 10 - 1)
		parse_feed_back(feed_back, abs_url)
	print('Done.')