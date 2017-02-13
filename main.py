import requests
import json
import re
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

def parse_first_html(zhihu_html_object, abs_url):
	soup = BeautifulSoup(zhihu_html_object.text, 'lxml')
	item_list = soup.find_all('div', attrs={'class' : 'feed-content'})
	for item in item_list:
		title = item.h2.a.text
		try:
			name = item.find('div', attrs = {'class':'zm-item-rich-text expandable js-collapse-body'}).get('data-author-name')
		except:
			name = item.find('div', attrs = {'class':'post-content'}).get('data-author-name')
		summary = item.find('div',attrs = {'class':'zh-summary summary clearfix'}).text
		link = item.find('div',attrs = {'class':'zh-summary summary clearfix'}).a.get('href')
		if 'https://' not in link:
			link += abs_url
		with open('zhihu.txt', 'a') as fp:
			fp.write(title)
			fp.write(name)
			fp.write(summary)
			fp.write(link)

def get_AJAX_html(AJAX_url, _xsrf):
	pass

class item(object):
	'''
		for every dymanic
	'''
	def __init__(self, title, name, summary, link):
		self.title = title
		self.name = name
		self.summary = summary
		self.link = link

	def __repr__(self):
		return '<This is a dymanic>'


if __name__ == '__main__':
	abs_url = 'https://www.zhihu.com'
	
	my_cookies = get_cookie()
	_xsrf = get_xsrf_from_cookies(my_cookies)
	zhihu_html_object = get_zhihu_html_object(abs_url, my_cookies)
	parse_first_html(zhihu_html_object, abs_url)
	print('Done.')