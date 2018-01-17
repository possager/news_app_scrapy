# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.loader.processors import TakeFirst



class NewsAppScrapyItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    # pass
    title = scrapy.Field(output_processor=TakeFirst())  # 标题
    content = scrapy.Field(output_processor=TakeFirst())  # 去噪后的存文本内容
    spider_time = scrapy.Field(input_processor=lambda x: int(x[0] * 1000), output_processor=TakeFirst())  # 爬虫爬取时间
    publish_time = scrapy.Field(output_processor=TakeFirst())  # 发布时间
    id = scrapy.Field(output_processor=TakeFirst())  # 在平台中的言论ID（如果是回复的话，有就填，没有就不填）
    publish_user_photo = scrapy.Field(output_processor=TakeFirst())  # 用户头像
    publish_user = scrapy.Field(output_processor=TakeFirst())  # 用户名
    url = scrapy.Field(output_processor=TakeFirst())  # （论坛的URL）||（论坛回复的URL）||（新闻的URL）

    img_urls = scrapy.Field()  # 图片urls,string数组类型
    publish_user_id = scrapy.Field(output_processor=TakeFirst())  # 用户id
    reply_count = scrapy.Field(output_processor=TakeFirst())  # 回复数

    read_count = scrapy.Field(output_processor=TakeFirst())  # 阅读量
    like_count = scrapy.Field(output_processor=TakeFirst())  # 赞成数
    publish_user_jsonid = scrapy.Field(output_processor=TakeFirst())  # 用户的jsonid(对应着用户json信息的命名：平台名称（或者英文）_用户id)
    txpath = scrapy.Field(output_processor=TakeFirst())  # 图片存放服务器(针对微信)
    reply_nodes = scrapy.Field()  # jsonArray类型变量,结构和当前json结构一样
    reproduce_count = scrapy.Field(output_processor=TakeFirst())  # 转载数
    ancestor_id = scrapy.Field(output_processor=TakeFirst())  # 祖先借点的ID（回复和回复的回复必填）
    parent_id = scrapy.Field(output_processor=TakeFirst())  # 父集ID（如果是回复就填，没有就不填）
    like_nodes = scrapy.Field()  # jsonArray类型变量，里面的结构和当前json结构一样
    video_urls = scrapy.Field()  # 视频urls,string数组类型
    is_pic = scrapy.Field(output_processor=TakeFirst())  # 是否包含图片(针对微信)
    dislike_count = scrapy.Field(output_processor=TakeFirst())  # 反对数

    #手机端app新闻的特有字段
    channelId=scrapy.Field()
    abstract=scrapy.Field()
    params=scrapy.Field()
    appname=scrapy.Field()
    channelName=scrapy.Field()