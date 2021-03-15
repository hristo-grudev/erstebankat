import json

import scrapy

from scrapy.loader import ItemLoader

from ..items import ErstebankatItem
from itemloaders.processors import TakeFirst

import requests

url = "https://www.erstegroup.com/bin/erstegroup/gemesgapi/feature/gem_site_de_www-erstegroup-com-de-es7/,"

base_payload = "{\"filter\":[{\"key\":\"path\",\"value\":\"/content/sites/at/eh/www_erstegroup_com/de/news-media" \
               "/presseaussendungen\"},{\"key\":\"tags\",\"value\":\"at:eh/news/Results,at:eh/news/CorporateNews," \
               "at:eh/news/CorporateBanking,at:eh/news/PeopleProsperity,at:eh/news/Innovation,at:eh/news/Personnel," \
               "at:eh/news/RetailBanking,at:eh/news/Research,at:eh/news/CEEInsights\"}],\"page\":%s,\"query\":\"*\"," \
               "\"items\":10,\"sort\":\"DATE_RELEVANCE\",\"requiredFields\":[{\"fields\":[\"teasers.NEWS_DEFAULT\"," \
               "\"teasers.NEWS_ARCHIVE\",\"teasers.newsArchive\"]}]} "
headers = {
  'Connection': 'keep-alive',
  'Pragma': 'no-cache',
  'Cache-Control': 'no-cache',
  'sec-ch-ua': '"Google Chrome";v="89", "Chromium";v="89", ";Not A Brand";v="99"',
  'sec-ch-ua-mobile': '?0',
  'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/89.0.4389.82 Safari/537.36',
  'Content-Type': 'application/json',
  'Accept': '*/*',
  'Origin': 'https://www.erstegroup.com',
  'Sec-Fetch-Site': 'same-origin',
  'Sec-Fetch-Mode': 'cors',
  'Sec-Fetch-Dest': 'empty',
  'Referer': 'https://www.erstegroup.com/de/news-media/presseaussendungen',
  'Accept-Language': 'en-US,en;q=0.9,bg;q=0.8',
  'Cookie': '3cf5c10c8e62ed6f6f7394262fadd5c2=38152618e0350b39d330076005a62c18; TCPID=1213111294510701302341; TC_PRIVACY=0@020@1@2@1615800586821@; TC_PRIVACY_CENTER=1; s_fid=00C06FD145DF4BEB-2142352E26C2FC79; s_cc=true; _cs_c=1; s_sq=%5B%5BB%5D%5D; _cs_cvars=%7B%221%22%3A%5B%22Page%20Name%22%2C%22presseaussendungen%22%5D%2C%222%22%3A%5B%22Page%20Title%22%2C%22Presseaussendungen%22%5D%2C%223%22%3A%5B%22Page%20Template%22%2C%22standardContentPage%22%5D%2C%224%22%3A%5B%22Language%22%2C%22de%22%5D%7D; _cs_id=6bb25d0a-a9f3-ad12-f708-63d5ee212bc8.1615800587.1.1615800619.1615800587.1.1649964587751.Lax.0; _cs_s=5.3; __CT_Data=gpv=2&ckp=tld&dm=erstegroup.com&apv_59_www56=2&cpv_59_www56=2'
}


class ErstebankatSpider(scrapy.Spider):
	name = 'erstebankat'
	start_urls = ['https://www.erstegroup.com/de/news-media/presseaussendungen']
	page = 0

	def parse(self, response):
		payload = base_payload % self.page
		data = requests.request("POST", url, headers=headers, data=payload)
		raw_data = json.loads(data.text)
		for post in raw_data['hits']['hits']:
			link = post['_source']['url']
			date = post['_source']['date']
			title = post['_source']['title']
			yield response.follow(link, self.parse_post, cb_kwargs={'date': date, 'title': title})
		if self.page < raw_data['hits']['total'] // 10:
			self.page += 1
			yield response.follow(response.url, self.parse, dont_filter=True)

	def parse_post(self, response, date, title):
		description = response.xpath(
			'(//div[@class="w-auto mw-full rte"])[position()>3]//text()[normalize-space()]').getall()
		description = [p.strip() for p in description]
		description = ' '.join(description).strip()

		item = ItemLoader(item=ErstebankatItem(), response=response)
		item.default_output_processor = TakeFirst()
		item.add_value('title', title)
		item.add_value('description', description)
		item.add_value('date', date)

		return item.load_item()
