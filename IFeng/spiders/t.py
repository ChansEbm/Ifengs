# -*- coding: utf-8 -*-
import math
from urllib.parse import urlencode

import demjson
import scrapy
from pydispatch import dispatcher
from scrapy import signals


class TSpider(scrapy.Spider):
    name = 't'
    start_urls = [
        'http://www.piaov.com/list/2.html', "http://www.piaov.com/list/4.html"]
    s = set()
    c = []

    def __init__(self):
        super(TSpider, self).__init__()
        dispatcher.connect(self.close, signal=signals.spider_closed)

    def parse(self, response):
        comment_detail = demjson.decode(response.text)
        count = comment_detail["count"]
        end_page = math.ceil(count / 20)

        meta = response.meta
        old_comments = meta.get("comments", [])
        comments = comment_detail['comments']
        self.c += comments
        comp = old_comments + comments
        meta.update(comments=comp)
        p = 2
        while p <= end_page:
            d = meta.get("dockey", {})
            d.update(p=str(p))

            meta = response.meta
            old_comments = meta.get("comments", [])
            comments = comment_detail['comments']
            self.c += comments
            comp = old_comments + comments
            meta.update(comments=comp)
            yield scrapy.Request(url='http://comment.ifeng.com/get.php?' + urlencode(d), meta=meta, callback=self.parse)
            p += 1

        yield scrapy.Request(url="https://www.baidu.com", callback=self.check, meta=meta)

    def start_requests(self):
        url = 'http://comment.ifeng.com/get.php?'
        d = {"orderby": "uptimes",
             "docUrl": "sub_34103412",
             "format": "json",
             "job": "1",
             "p": "1",
             "skey": "6e83b1"
             }
        yield scrapy.Request(url=url + urlencode(d), meta={"dockey": d})

    def check(self, response):
        self.c = response.meta.get("comments", [])
        pass

    def close(self, spider):
        print(self.c)
        print(len(self.c))
        pass
