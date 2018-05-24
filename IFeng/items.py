# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# https://doc.scrapy.org/en/latest/topics/items.html

import scrapy


class IfengItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # 网页连接
    article_url = scrapy.Field()
    # 标题
    doc_name = scrapy.Field()
    # 类别
    category = scrapy.Field()
    # 上传时间
    upload_time = scrapy.Field()
    # 来源
    src_from = scrapy.Field()
    # 作者
    author = scrapy.Field()
    # 参与人数
    count_of_join = scrapy.Field()
    # 评论人数
    count_of_comment = scrapy.Field()
    # 核心内容，摘要
    summary = scrapy.Field()
    # 主体部分
    article_content = scrapy.Field()
    # 评论list
    comments = scrapy.Field()
    # 点评list
    fav = scrapy.Field()
    pass
