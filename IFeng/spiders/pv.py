# -*- coding: utf-8 -*-
import scrapy


class PvSpider(scrapy.Spider):
    name = 'pv'
    allowed_domains = ['www.piaov.com']
    start_urls = ['http://www.piaov.com/']

    def parse(self, response):
        names = response.xpath("//ul[@class='mlist']//li/a/@title").extract()
        on = response.meta.get("names", [])
        cmp_names = on + names
        for p in range(2, 7):
            yield scrapy.Request(url='http://www.piaov.com/list/7_{}.html'.format(p),
                                 meta={"names": cmp_names},
                                 callback=self.parse)

        yield scrapy.Request("http://www.piaov.com", meta={"names": cmp_names}, callback=self.parse_item)

    def parse_item(self, response):
        pass

    def start_requests(self):
        yield scrapy.Request(url='http://www.piaov.com/list/7.html')
