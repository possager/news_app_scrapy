#_*_coding:utf-8_*_
import scrapy
from scrapy_redis.spiders import Spider
import pymongo
import json
import datetime
import time
import urllib
import re
from datetime import timedelta
import pickle






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
                    yield scrapy.Request(url=thisboard_index['url'],headers=self.headers,meta={'meta_from_index':thisboard_index},callback=self.parse_index_from_board_movie)
                except:
                    pass
            else:

                try:
                    yield scrapy.Request(url=thisboard_index['url'],headers=self.headers,meta={'meta_from_index':thisboard_index},callback=self.parse_index_from_board_nomovie)
                except:
                    pass


    def parse_index_from_board_nomovie(self,response):
        print response.url
        data_meta_from_board=response.meta
        if len(response.body)<10:
            return


        # with open('pickle_dict/response_index_board_nomovie','w+') as f:
        #     pickle.dump(obj=response.selector,file=f)

        for one_url in response.xpath('//body/div'):
            thisurl=one_url.xpath('.//div[@class="t_news_bg"]/div/a/@href').extract()
            publish_user=one_url.xpath('//p/a/@href').extract()
            title=one_url.xpath('//a/text()').extract()
            try:
                publish_time=one_url.xpath('.//a/span/text()').extract()
            except Exception as e:
                publish_time='00:00:00'

            try:
                publish_time_date=one_url.xpath('.//span/text()').extract_first()
                if u'天前' in publish_time_date:
                    publish_time_date = publish_time_date.replace(u'天前', '')
                    date_now = datetime.datetime.now()
                    date_now2 = date_now - timedelta(days=int(publish_time_date))
                    publish_time_date = date_now2
                    publish_time_date = str(publish_time_date.strftime('%Y-%m-%d %H:%M'))
                elif u'小时前' in publish_time_date:
                    publish_time_date = publish_time_date.replace(u'小时前', '')
                    date_now = datetime.datetime.now()
                    date_now2 = date_now - timedelta(hours=int(publish_time_date))
                    publish_time_date = date_now2
                    publish_time_date = str(publish_time_date.strftime('%Y-%m-%d %M:%H:%S'))
                elif u'分钟前' in publish_time_date:
                    publish_time_date = publish_time_date.replace(u'分钟前', '')
                    date_now = datetime.datetime.now()
                    date_now2 = date_now - timedelta(minutes=int(publish_time_date))
                    publish_time_date = date_now2
                    publish_time_date = str(publish_time_date.strftime('%Y-%m-%d %M:%H:%S'))
                else:
                    date_now=datetime.datetime.now()
                    publish_time_date=date_now.strftime('%Y-%m-%d %M:%H:%S')
            except Exception as e:
                try:
                    publish_time_date=one_url.xpath('//span/text()').extract()
                except Exception as e:
                    print e
                try:
                    if len(one_url.xpath('//span/text()'))==10:
                        publish_time_date=one_url.xpath('//span/text()').extract()
                    else:
                        continue
                except:
                    continue

            publish_time = publish_time_date + ' ' + publish_time + ':00'
            id=response.xpath('//h2/a/@id')







    def parse_index_from_board_movie(self,response):
        print response.url




    def parse_content_from_index_nomovie(self,response):
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





    def parse_index_from_board_movie(self,response):
        data_meta_from_index=response.meta['meta_from_index']