# -*- coding: utf-8 -*-
import math
from urllib.parse import urlencode

import demjson
import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule

from IFeng.utils import formatter
from IFeng.utils.formatter import parse_model, parse_content


class IfengSpider(CrawlSpider):
    name = 'ifeng'
    allowed_domains = ['www.ifeng.com', 'news.ifeng.com', 'comment.ifeng.com', 'survey.news.ifeng.com']
    start_urls = ['http://www.ifeng.com/']

    rules = (
        # 只解析历史page
        Rule(LinkExtractor(allow=r'/history', restrict_xpaths=r'//div[@id="viceNav"]'), follow=True),
        # listpage下的各个子标签
        Rule(LinkExtractor(allow=r'/listpage/\d+/\d+/list.shtml', restrict_xpaths=r'//div[@id="col_wbf"]'),
             follow=True),
        # 下一页
        Rule(LinkExtractor(allow=r'/listpage/\d+/\d+/\d+/\d+/list.shtml', restrict_xpaths=r'//a[@id="pagenext"]'),
             follow=True),
        # 解析主体
        Rule(LinkExtractor(allow=r'/a/\d+/\d+_\d+.shtml',
                           restrict_xpaths=r'//div[@class="yc_con"]|//div[@class="box650"]'),
             callback='parse_item',
             follow=False),
    )

    def parse_item(self, response):
        keyword_dict, g_list = formatter.to_dict1(response)

        comment_url = 'http://comment.ifeng.com/get.php?'
        comment_dict = {k: v for k, v in keyword_dict.items() if k == "commentUrl" or k == "skey"}
        comment_dict.update(
            docUrl=comment_dict.pop("commentUrl") if 'commentUrl' in comment_dict else keyword_dict.get("docUrl", ""))
        comment_dict.update({"format": "json", "job": "1", "p": "1", "orderby": "uptimes"})
        meta = {"comment_dict": comment_dict}
        doc_name = keyword_dict.get("docName", "")
        summary = keyword_dict.get('summary', "")
        category = "历史图片"
        author = ""
        article_dict = dict(article_url=response.url, doc_name=doc_name, summary=summary, category=category,
                            author=author)
        # 表明这是图集,图集是没有点赞的
        if g_list:
            upload_time = response.xpath('//div[@class="titL"]//span/text()')
            article_dict.update(article_content=g_list, upload_time=upload_time)
        else:
            # 文章有点赞
            meta.update(fav=True)
            # 解析文章主体

            # 一般模块
            p_time = response.xpath('//p[@class="p_time"]')
            # 栏目模块
            yc_tit = response.xpath('//div[@class="yc_tit"]')
            models = parse_model(p_time, yc_tit)
            upload_time = models[0]
            src_from = models[1]
            author = models[2]

            category = response.xpath(
                '//div[contains(@class,"theCurrent cDGray")]//a[@class="ss_none"]/text()'
                '|'
                '//div[class="yc_tit"]//a/text()').extract_first()
            ac_start = 1 if summary else 0
            main_content = response.xpath('//div[@id="main_content"]')
            yc_tit_text = response.xpath('//div[@id="yc_con_txt"]')
            article_content = parse_content(main_content=main_content, yc_tit_text=yc_tit_text)
            article_dict.update(upload_time=upload_time, src_from=src_from, category=category, author=author,
                                article_content=article_content)
        meta.update(article_dict=article_dict)
        yield scrapy.Request(url=comment_url + urlencode(comment_dict), meta=meta, callback=self.parse_comment)

    def parse_comment(self, response):
        meta = response.meta
        fav = meta.get("fav", False)
        comment_detail = demjson.decode(response.text)
        count_of_comments = comment_detail["count"]
        comment_dict = meta.get("comment_dict", {})
        comments = comment_detail["comments"]
        old_comments = meta.get("article_dict", {}).get("comments", [])
        meta.get("article_dict", {}).update(comments=(old_comments + comments))

        end_page = int(math.ceil(count_of_comments / 20)) + 1
        for p in range(2, end_page):
            comment_dict.update(p=p)
            yield scrapy.Request(url="http://comment.ifeng.com/get.php?" + urlencode(comment_dict),
                                 callback=self.parse_comment, meta=meta)

        # 有点赞模块，把点赞数抓下来
        if fav:
            accumulator_list = ['good', 'adore', 'smile', 'cry', 'boring', 'angry']
            accumulator_base_url = 'http://survey.news.ifeng.com/getaccumulator_ext.php?format=json&'
            accumulator_params = ""
            for ac in accumulator_list:
                accumulator_params += "key[]={url}?{ac}".format(url=meta.get('article_dict', {}).get('article_url', ""),
                                                                ac=ac)
                accumulator_params += "&" if ac is not 'angry' else ''
            accumulator_url = accumulator_base_url + accumulator_params
            yield scrapy.Request(url=accumulator_url, method='GET', meta=meta, callback=self.parse_fav)
        # 图集就直接yield item
        else:
            pass

    def parse_fav(self, response):
        pass
