import scrapy
import json
import random
class GithubSearchSpider(scrapy.Spider):
	name = "github_search_spider"
	initialized = False
	def initialize(self, test_mode=False, test_mode_json=None):
		#handling initialization
		if not self.initialized:
			self.parse_input_json(test_mode, test_mode_json)
			self.select_proxy()
			self.initialized = True
	def parse_input_json(self, test_mode, test_mode_json):
		#reading json and setting parameters
		if test_mode:
			json_string = test_mode_json
		else:
			with open(self.jsoninput, "r") as json_file_to_read:
				json_string = open(self.jsoninput, "r").read()
		json_data = json.loads(json_string)
		print(json_data)
		self.keywords = json_data["keywords"]
		self.proxies = json_data["proxies"]
		self.type_to_look = json_data["type"]
	def select_proxy(self):
		#randomly selecting a proxy
		self.selected_proxy = "http://" + random.choice(self.proxies)
		print("Selected Proxy:", self.selected_proxy)
	def get_main_url(self):
		#generating the search URL
		joined_query = "+".join(self.keywords)
		return f"https://github.com/search?q={joined_query}&type={self.type_to_look}"
	def start_requests(self):
		#actually creating the request to get the previous URL
		self.initialize()
		main_url = self.get_main_url()
		yield scrapy.Request(main_url, callback=self.parse_main_search, meta={"proxy": self.selected_proxy})
	def parse_main_search(self, response):
		#switching based on case
		if self.type_to_look == "Repositories":
			#finding all the repository links
			repository_links = response.css('ul.repo-list a.v-align-middle::attr(href)').getall()
			print("Found repo links:", repository_links)
			#converting the partial URLs to full URLs
			full_repository_links = [response.urljoin(link) for link in repository_links]
			for link in full_repository_links:
				print("Doing link:", link)
				#recursively entering the found links, to grab the additional data required
				yield scrapy.Request(link, callback=self.parse_specific_repository, meta={"proxy": self.selected_proxy})
		elif self.type_to_look == "Issues":
			#finding all the issues links
			issues_links = response.css('div.issue-list-item h3.text-normal a::attr(href)').getall()
			print("Found issues links:", issues_links)
			#converting the partial URLs to full URLs
			full_issues_links = [response.urljoin(link) for link in issues_links]
			for link in full_issues_links:
				print("Doing link:", link)
				#yielding the urls to be saved
				yield {"url": link}
		elif self.type_to_look == "Wikis":
			#finding all the wikis links
			wikis_links = response.css('#wiki_search_results div.d-inline-block a:not([class^="h5"])::attr(href)').getall()
			print("Found wikis links:", wikis_links)
			#converting the partial URLs to full URLs
			full_wikis_links = [response.urljoin(link) for link in wikis_links]
			for link in full_wikis_links:
				print("Doing link:", link)
				#yielding the urls to be saved
				yield {"url": link}

	def parse_specific_repository(self, response):
		#entering specific repository to get owner and languages
		#getting the owner
		current_owner = response.css('span.author a.url::text').get()
		print("Repo owner:", current_owner)
		#getting all the languages
		languages = response.css('ol.repository-lang-stats-numbers span.lang::text').getall()
		print("-------LANG", languages)
		#getting all the language percentages
		percentages = response.css('ol.repository-lang-stats-numbers span.percent::text').getall()
		zipped_percentage_dict = {}
		#changing the data structure and converting the strings to floats
		for lang, percent in zip(languages, percentages):
			print("Language:", lang, "Percentage:", percent[:-1])
			zipped_percentage_dict[lang] = float(percent[:-1])
		#yielding the repo data to be saved
		yield {
			"url": response.url,
			"extra": {
				"owner": current_owner,
				"language_stats": zipped_percentage_dict
			}
		}
