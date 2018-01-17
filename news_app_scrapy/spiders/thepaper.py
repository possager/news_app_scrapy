#_*_coding:utf-8_*_
import scrapy
from scrapy_redis.spiders import Spider
import pymongo
import json
import datetime
import time
import urllib
import re



class thepaper(scrapy.Spider):
    name = 'thepaper'
    mongoClient=pymongo.MongoClient('178.16.7.86', 27017)#178.16.7.86
    jiemianCOL=mongoClient['appnewsMongodb']
    jiemianDOC=jiemianCOL['channellist']

    headers = {
        'User-Agent': 'Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1',
        'Connection': 'close'
    }


    def start_requests(self):
        urls = []
        urlList = self.jiemianDOC.find({'appName': 'thepaper', 'recommend': {'$gt': 0}})
        for url_dict in urlList:
            one_board_info = {
                'url': url_dict['url'],
                'channelId': url_dict['channelId'],
                'abstract': None,
                'params': None,
                'appname': 'thepaper',
                'channelName': url_dict['channelName']
            }

            yield scrapy.Request(url=url_dict['url'],headers=self.headers,meta={'info_from_start':one_board_info},callback=self.parse_index_from_board)#从板块的分类方法到索引列表的分类方法。


    def parse_index_from_board(self, response):
        data_meta_from_index=response.meta['info_from_start']

        print response.url
        Re_pattern = re.compile(r'data	:	\"(.*?)\".*?Math\.random\b')
        datare = Re_pattern.findall(response.body)

        try:
            url_in_content = datare[0]
        except Exception as e:
            return
        if 'http://m.thepaper.cn/channel_26916' in response.url:
            nexturl = 'http://www.thepaper.cn/load_index.jsp?' + url_in_content  # 发现手机端的数据获得地更多一些,电脑端http://m.thepaper.cn/load_channel.jsp?
        else:
            nexturl = 'http://m.thepaper.cn/load_channel.jsp?' + url_in_content

        #通过i来控制爬取多少页数据。
        for i in range(2):
            thisboard_index={
                'url': nexturl+str(i),
                'channelName': data_meta_from_index['channelName'],
                'channelId': response.url.split('/')[-1],
                'appname': 'thepaper',
                'abstract': None,
                'params': None,
            }
            if 'http://www.thepaper.cn/load_index.jsp?' in thisboard_index['url']:
                try:
                    yield scrapy.Request(url=thisboard_index['url'],headers=self.headers,meta={'meta_from_index':thisboard_index},callback=self.parse_content_from_index_movie)
                except:
                    pass
            else:
                # thread_in_while=threading.Thread(target=get_index_inside_wenben,args=(data_in_while,))
                # thread_in_while=process.Process(target=get_index_inside_wenben,args=(data_in_while,))
                try:
                    yield scrapy.Request(url=thisboard_index['url'],headers=self.headers,meta={'meta_from_index':thisboard_index},callback=self.parse_content_from_index_wenben)
                except:
                    pass


    def parse_content_from_index_wenben(self,response):
        data_meta_from_index=response.meta['meta_from_index']

        content_div=response.xpath('//div[@class="news_content"]//div[@class="news_part_father"]')
        content_div_str=str(content_div)
        like_count=response.xpath('//a[@id="news_praise"]/text()').re('(\d+)')

        if like_count:
            like_count_value = int(like_count[0].text.strip())
        else:
            like_count_value = 0

        vedio_urls=response.xpath('//video/source/@src').extract()

        data_meta_from_index['content'] = content_div_str
        data_meta_from_index['like_count'] = like_count_value
        data_meta_from_index['video_urls'] = vedio_urls
        # data_meta_from_index['source'] = source



        url_cmt = 'http://app.thepaper.cn/clt/jsp/v3/contFloorCommentList.jsp'
        post_data = {
            'WD-UUID': '861557177515977',
            'WD-CLIENT-TYPE': '04',
            'WD-UA': 'oneplus_a3010_android',
            'WD-VERSION': '4.4.6',
            'WD-CHANNEL': '360sjzs',
            'WD-RESOLUTION': '720*1256',
            'userId': '2704158',
            'WD-TOKEN': 'd2d2344c928de46787d06b6574c9fea0',
        }
        post_data['c']=data_meta_from_index['id']
        yield scrapy.FormRequest(url=url_cmt)





    def parse_content_from_index_movie(self,response):
        data_meta_from_index=response.meta['meta_from_index']