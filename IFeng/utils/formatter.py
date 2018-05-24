import json
import re

import demjson
import six
from requests_html import HTML


def to_dict(htmltext):
    # if not isinstance(htmltext, six.string_types):
    #     raise TypeError("Except str got {}".format(type(htmltext).__name__))
    script_str = 'define("detail"'
    script_str1 = "define('detail'"
    text = HTML(html=htmltext)
    try:
        key_word_obj = text.find("script", containing=script_str)[0].text
    except:
        key_word_obj = text.find("script", containing=script_str1)[0].text
    key_word_obj = key_word_obj.replace("\\", "")
    key_word = re.search(r'return(.*?})', key_word_obj, re.S).group(1)
    key_word = key_word.replace("\\", "")
    keyword_dict = demjson.decode(json.dumps(key_word, ensure_ascii=False))
    if isinstance(keyword_dict, str):
        keyword_dict = demjson.decode(keyword_dict)
    print(type(keyword_dict))
    return keyword_dict
    # , g_list(text)


def to_dict1(response):
    global keyword_dict
    script_str = 'define("detail"'
    script_str1 = "define('detail'"
    key_word_obj = response.xpath("//script/text()[contains(.,'{}')]".format(script_str))
    if not any(key_word_obj):
        key_word_obj = response.xpath('//script/text()[contains(.,"{}")]'.format(script_str1))
    k_dict = key_word_obj.extract_first()
    key_word = re.search(r'return(.*?})', k_dict, re.S).group(1)
    try:
        keyword_dict = demjson.decode(key_word)
    except:
        pass
    return keyword_dict, g_list(response)


def g_list(response):
    # gl = text.find('script', containing='G_list')
    gl = response.xpath("//script/text()[contains(.,'G_listdata')]").extract_first()
    if gl:
        pic_json = re.search(r'\[.*\]', gl, re.S).group()
        try:
            g_list = demjson.decode(pic_json)
        except:
            pass
        return g_list


def parse_model(p_time, yc_tit):
    upload_time = p_time.xpath('.//span[@class="ss01"]/text()').extract_first()
    upload_time = upload_time if upload_time else yc_tit.xpath('./p/span[1]/text()').extract_first()

    src_from = p_time.xpath('.//a/text()').extract_first()
    src_from = src_from if src_from else yc_tit.xpath('./p/a/text()').extract_first()

    author = p_time.xpath('.//span[@itemprop="author"]/span/text()').extract_first()
    author = author if author else yc_tit.xpath('./p/span[2]/text()').extract_first()

    return upload_time, src_from, author


def parse_content(main_content, yc_tit_text):
    article_content = main_content.xpath(".//p[not(@class)]/text()").extract()

    return article_content if article_content else yc_tit_text.xpath(".//p[not(@class)]/text()").extract()
