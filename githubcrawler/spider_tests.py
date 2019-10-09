import unittest
import json
from spiders.search_spider import GithubSearchSpider
from scrapy.http import TextResponse

class TestParsers(unittest.TestCase):

	def setUp(self):
		self.spider_to_test = GithubSearchSpider()
	def init_spider(self, keywords, proxies, type_to_look):
		object_to_serialize = {
			"keywords": keywords,
			"proxies": proxies,
			"type": type_to_look
		}
		serialized_json = json.dumps(object_to_serialize)
		self.spider_to_test.initialize(test_mode=True, test_mode_json=serialized_json)
	def test_json_input_parser(self):
		#testing that the parameters in the input json, are available for the spider object.
		keywords = ["aaa", "bbb", "ccc"]
		proxies = ["1.2.3.4:5678", "192.168.1.1:8000"]
		type_to_look = "Issues"
		self.init_spider(keywords, proxies, type_to_look)
		self.assertEqual(self.spider_to_test.keywords, keywords)
		self.assertEqual(self.spider_to_test.proxies, proxies)
		self.assertEqual(self.spider_to_test.type_to_look, type_to_look)
	def test_proxy_selection(self):
		keywords = ["aaa", "bbb", "ccc"]
		proxies = ["1.2.3.4:5678", "192.168.1.1:8000", "192.168.1.2:8000", "192.168.1.3:8000"]
		type_to_look = "Issues"
		self.init_spider(keywords, proxies, type_to_look)
		#testing proxy is in list of proxies.
		self.assertIn(self.spider_to_test.selected_proxy, [f"http://{proxy}" for proxy in proxies])
		#testing random proxy selection
		start_proxy = self.spider_to_test.selected_proxy
		found_different_proxy = False
		retry_count = 100
		while retry_count:
			self.spider_to_test.select_proxy()
			retry_count -= 1
			if self.spider_to_test.selected_proxy != start_proxy:
				break
				print("Found different proxy!")
		self.assertNotEqual(start_proxy, self.spider_to_test.selected_proxy)
	def test_initial_request_parameters(self):
		#checking the initial request actually makes sense
		keywords = ["aaa", "bbb", "ccc"]
		proxies = ["1.2.3.4:5678", "192.168.1.1:8000"]
		type_to_look = "Issues"
		object_to_serialize = {
			"keywords": keywords,
			"proxies": proxies,
			"type": type_to_look
		}
		self.init_spider(keywords, proxies, type_to_look)
		#getting the first request made.
		first_request = next(self.spider_to_test.start_requests())
		#checking the url is okay
		self.assertEqual(first_request.url, "https://github.com/search?q=" + "+".join(self.spider_to_test.keywords) + "&type=" + self.spider_to_test.type_to_look)
		#checking the proxy will be used
		self.assertEqual(first_request.meta['proxy'], self.spider_to_test.selected_proxy)
		#checking the callback
		self.assertEqual(first_request.callback, self.spider_to_test.parse_main_search)
	def test_parser_type_issues(self):
		#testing the "Issues" parsing
		keywords = ["openstack", "nova", "css"]
		proxies = ["1.2.3.4:5678", "192.168.1.1:8000"]
		type_to_look = "Issues"
		object_to_serialize = {
			"keywords": keywords,
			"proxies": proxies,
			"type": type_to_look
		}
		self.init_spider(keywords, proxies, type_to_look)
		current_response = TextResponse(url=self.spider_to_test.get_main_url(), body=open("test_files/issues.html", "r").read(), encoding="utf-8")
		results = self.spider_to_test.parse_main_search(current_response)
		results_list = []
		results_compare_list = [
		{'url': 'https://github.com/novnc/websockify/issues/180'},
		{'url': 'https://github.com/altai/nova-billing/issues/1'},
		{'url': 'https://github.com/rclone/rclone/issues/2713'},
		{'url': 'https://github.com/sfPPP/openstack-note/issues/8'},
		{'url': 'https://github.com/hellowj/blog/issues/37'},
		{'url': 'https://github.com/bblfsh/python-driver/issues/202'},
		{'url': 'https://github.com/moby/moby/issues/19758'},
		{'url': 'https://github.com/YumaInaura/YumaInaura/issues/1322'},
		{'url': 'https://github.com/jupyterhub/the-littlest-jupyterhub/issues/108'},
		{'url': 'https://github.com/aaronkurtz/gourmand/pull/35'}]
		for result in results:
			results_list.append(result)
		self.assertEqual(results_list, results_compare_list)

	def test_parser_type_wikis(self):
		#testing the "Wikis" parsing
		keywords = ["openstack", "nova", "css"]
		proxies = ["1.2.3.4:5678", "192.168.1.1:8000"]
		type_to_look = "Wikis"
		object_to_serialize = {
			"keywords": keywords,
			"proxies": proxies,
			"type": type_to_look
		}
		self.init_spider(keywords, proxies, type_to_look)
		current_response = TextResponse(url=self.spider_to_test.get_main_url(), body=open("test_files/wikis.html", "r").read(), encoding="utf-8")
		results = self.spider_to_test.parse_main_search(current_response)
		results_list = []
		results_compare_list = [
		{'url': 'https://github.com/vault-team/vault-website/wiki/Quick-installation-guide'},
		{'url': 'https://github.com/iwazirijr/wiki_learn/wiki/Packstack'},
		{'url': 'https://github.com/marcosaletta/Juno-CentOS7-Guide/wiki/2.-Controller-and-Network-Node-Installation'},
		{'url': 'https://github.com/MirantisDellCrowbar/crowbar/wiki/Release-notes'},
		{'url': 'https://github.com/dellcloudedge/crowbar/wiki/Release-notes'},
		{'url': 'https://github.com/eryeru12/crowbar/wiki/Release-notes'},
		{'url': 'https://github.com/rhafer/crowbar/wiki/Release-notes'},
		{'url': 'https://github.com/jamestyj/crowbar/wiki/Release-notes'},
		{'url': 'https://github.com/vinayakponangi/crowbar/wiki/Release-notes'},
		{'url': 'https://github.com/kingzone/node/wiki/Modules'}]
		for result in results:
			results_list.append(result)
		#print(results_list)
		self.assertEqual(results_list, results_compare_list)

	def test_parser_type_repositories(self):
		#testing the "Repositories" parsing
		#this only checks that the parser obtains all the repo URLs,
		#that the selected proxy is being used, 
		#and that the following callback points to the right function.
		keywords = ["openstack", "nova", "css"]
		proxies = ["1.2.3.4:5678", "192.168.1.1:8000"]
		type_to_look = "Repositories"
		object_to_serialize = {
			"keywords": keywords,
			"proxies": proxies,
			"type": type_to_look
		}
		self.init_spider(keywords, proxies, type_to_look)
		current_response = TextResponse(url=self.spider_to_test.get_main_url(), body=open("test_files/repositories.html", "r").read(), encoding="utf-8")
		results = self.spider_to_test.parse_main_search(current_response)
		results_list = []
		results_compare_list = [
		"https://github.com/atuldjadhav/DropBox-Cloud-Storage",
		"https://github.com/michealbalogun/Horizon-dashboard"]
		for result in results:
			results_list.append(result)
		for index, yielded_request in enumerate(results_list):
			print("Testing url/callback:", yielded_request.url)
			self.assertEqual(yielded_request.url, results_compare_list[index])
			self.assertEqual(yielded_request.callback, self.spider_to_test.parse_specific_repository)
			self.assertEqual(yielded_request.meta['proxy'], self.spider_to_test.selected_proxy)
	def test_parser_individual_repository(self):
		#this tests the individual repository parsing
		#where the owner and language data is obtained.
		keywords = ["openstack", "nova", "css"]
		proxies = ["1.2.3.4:5678", "192.168.1.1:8000"]
		type_to_look = "Repositories"
		object_to_serialize = {
			"keywords": keywords,
			"proxies": proxies,
			"type": type_to_look
		}
		self.init_spider(keywords, proxies, type_to_look)
		current_response = TextResponse(url=self.spider_to_test.get_main_url(), body=open("test_files/individual_repository.html", "r").read(), encoding="utf-8")
		results = self.spider_to_test.parse_specific_repository(current_response)
		results_list = []
		results_compare_list = [
		{'url': 'https://github.com/search?q=openstack+nova+css&type=Repositories',
		'extra': {
			'owner': 'atuldjadhav',
			'language_stats': {
				'CSS': 52.0,
				'JavaScript': 47.2,
				'HTML': 0.8}
				}
		}]
		for result in results:
			results_list.append(result)
		self.assertEqual(results_list, results_compare_list)

if __name__ == '__main__':
	unittest.main()