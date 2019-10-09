# scrapy-github-search
Small crawler for GitHub search.

This is a small program, using Scrapy that crawls the Github search, from the first page of the search results with selected keywords, one of the following things:
  - Repositories: The crawler gets the URL of each repository, its owner, and all the languages used (including the percentage of each one)
  - Issues: URLs only.
  - Wikis: URLs only.

## Instructions to use

### Requirements (tip: use a virtual environment)
    - Python 3.6 or higher (f-strings are used)
    - Scrapy

After fulfilling both of these requirements, just do:

	`git clone https://github.com/fabrizziop/scrapy-github-search.git`

and enter the created directory.

#### Usage Syntax

From the main directory, use:

`scrapy crawl github_search_spider -a jsoninput="INPUTPARAMS.json" -o "OUTPUTDATA.json"`

`INPUTPARAMS.json` and `OUTPUTDATA.json` are name placeholders, you must change them, so `INPUTPARAMS.json` is the file name where the desired parameters for the crawl are set, and `OUTPUTDATA.json` the file name where the collected data will be saved.

Note: Please be aware that if there is already data inside `OUTPUTDATA.json`, scrapy will just append the results, and you probably will end up with invalid JSON data. 

##### Example `INPUTPARAMS.json` contents:

```
{
  "keywords": [
    "openstack",
    "nova",
    "css"
  ],
  "proxies": [
    "98.109.114.151:80",
    "157.245.57.147:8080",
    "80.211.135.240:8080"
  ],
  "type": "Repositories"
}
```

	- Keywords: One or more keywords to search.
	- Proxies: One or more proxies to use (selected randomly at initialization).
	- Type: "Repositories" or "Issues or "Wikis", nothing else is supported right now.

##### Example `OUTPUTDATA.json` contents:
```
[
	{"url": "https://github.com/michealbalogun/Horizon-dashboard", 
	"extra": {
		"owner": "michealbalogun",
		"language_stats": {
			"Python": 100.0
			}
		}
	},
	{"url": "https://github.com/atuldjadhav/DropBox-Cloud-Storage",
	"extra": {
		"owner": "atuldjadhav",
		"language_stats": {
			"CSS": 52.0,
			"JavaScript": 47.2,
			"HTML": 0.8
			}
		}
	}
]
```

An example input file, `input_01.json` is included in the repo's root folder.

#### Running Tests

Enter `githubcrawler/` and from there run the `spider_tests.py` script. Tests are run on both the spider initialization, and on the parsers (using stored html files included).
