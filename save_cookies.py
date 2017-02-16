import requests
import re
import json
'''
import time
from bs4 import BeautifulSoup
'''
abs_url = 'https://www.zhihu.com/'
headers = {
	'User-Agent':'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'
#	'Host':'www.zhihu.com',
#	'Referer':'https://www.zhihu.com/',
#	'Upgrade-Insecure-Requests':'1'
#只要模拟'User-Agent'就行了
}
def get_xsrf(abs_url):

	global headers	
	html = requests.get(abs_url, headers = headers).text
#	before = time.time()
	xsrf_instance = re.compile(r'<input type="hidden" name="_xsrf" value="(.*?)"')
	_xsrf = re.findall(xsrf_instance, html)[0]
#	use_time = time.time() - before
#	print('Time:%s' %use_time)
	return _xsrf

'''
def test(abs_url):
	header = {
	'User-Agent':'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/32.0.1667.0 Safari/537.36'
}
	html = requests.get(abs_url, headers = header).text
	before = time.time()
	soup = BeautifulSoup(html,"lxml")
	_xsrf = soup.find_all('input', attrs={'name':'_xsrf'})
	use_time = time.time() - before
	print('Time:%s' %use_time)
	print(_xsrf)
这种方法对只需要_xsrf来说效率太低
'''
def login(abs_url, _xsrf,password, phone_num):
	login_url = abs_url + 'login/phone_num'
	global headers
	data = {
	'_xsrf':_xsrf,
	'password':password,
	'captcha_type':'cn',
	'phone_num':phone_num
}
	r = requests.post(login_url, data=data, headers = headers)
	return r

def cookies_to_json(abs_url,_xsrf,password,phone_num):
	'''
		get cookies and save in json type
	'''
	r_1 = login(abs_url, _xsrf, password, phone_num)
	r_2 = requests.get('https://www.zhihu.com', headers = headers,cookies = r_1.cookies)
	r_2_cookies_dict = requests.utils.dict_from_cookiejar(r_2.cookies)
	cookies = requests.utils.add_dict_to_cookiejar(r_1.cookies, r_2_cookies_dict)
	my_cookies_dict = requests.utils.dict_from_cookiejar(cookies)
	cookies_json = json.dumps(my_cookies_dict)
	with open('cookies.json', 'w') as fp:
		fp.write(cookies_json)
	print(r_2.cookies['_xsrf'])

if __name__ == '__main__':
#	test(abs_url)
	phone_num = input('Phone number:')
	password = input('Password:')
	_xsrf = get_xsrf(abs_url)
	print(_xsrf)
	cookies_to_json(abs_url, _xsrf, password, phone_num)
	
