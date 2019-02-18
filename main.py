import os
import sys

from scrapy.cmdline import execute
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

if __name__ == '__main__':
    # debug single spider
    sys.path.append(os.path.abspath(__file__))
    execute('scrapy crawl CZ'.split())

    # # execute all the spider
    # os.environ.setdefault('SCRAPY_SETTINGS_MODULE', 'airline_tickets.settings')  # must load the project settings first
    # process = CrawlerProcess(get_project_settings())
    # for spider_name in process.spider_loader.list():
    #     # print(spider_name)
    #     process.crawl(spider_name)
    # process.start()
