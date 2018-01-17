#_*_coding:utf-8_*_
import scrapy
from scrapy_redis.spiders import Spider
import pymongo
import json
import datetime
import time
import urllib
import re




class jiemian(Spider):
    name = 'jiemian'

    headers = {
        'User-Agent': 'JiemianNews/5.1.0 (android; android 4.4.4; ONEPLUS A3010)',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'appapi.jiemian.com',
        'Connection': 'close'
    }

    client=pymongo.MongoClient('178.16.7.86',27017)
    COL=client['appnewsMongodb']
    DOC=COL['channellist']


    def start_requests(self):
        index_url_list=[]

        urlList=self.DOC.find({'appName': 'JieMianXinWen', 'recommend': {'$gt': 0}})
        for url_dict in urlList:
            one_board_info = {
                'url': url_dict['url'],
                'channelId': url_dict['channelId'],
                'abstract': None,
                'params': None,
                'appname': 'JieMianXinWen',
                'channelName': url_dict['channelName']
            }
            index_url_list.append(one_board_info)

        for index_info in index_url_list:
            yield scrapy.Request(url=index_info['url'],meta={'info_from_board':index_info},callback=self.parse_index_from_board,headers=self.headers)


    def parse_index_from_board(self,response):
        print response.url
        index_meta=response.meta['info_from_board']
        channelId = index_meta['channelId']
        channelName = index_meta['channelName']

        datajson=json.loads(response.body)

        index_list= datajson['result']['list']

        for one_index in index_list:

            try:
                article=one_index['article']
            except:
                continue

            id=article['ar_id']
            abstract = article['ar_sum']
            title = article['ar_tl']  # title
            reply_count = article['ar_cmt']  # 评论数
            read_count = article['ar_hit']  # 点击数
            url = article['ar_surl']  # url
            publish_user = article['ar_an']  # publish_user
            publicTimestamp = article['ar_pt']
            try:
                if u'w' in read_count:
                    read_count=float(str(read_count.replace(u'w','')))
                    read_count=int(read_count*1000)
            except Exception as e:
                read_count=0
                pass

            one_news_dict = {
                'id': str(id),
                'title': str(title.encode('utf-8')),
                'reply_count': reply_count,
                'read_count': read_count,
                'url': str(url),
                'publish_user': str(publish_user.encode('utf-8')),
                'channelId': str(channelId),
                'publicTimestamp': int(str(publicTimestamp)),
                'channelName': channelName,
                'abstract': str(abstract.encode('utf-8')),
                'params': None,
                'appname': 'JieMianXinWen',
                'spider_time': datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }

            host='appapi.jiemian.com'
            url = 'http://' + host + '/v4/5.1.0/10001/article/' + str(
                id) + '.json?code_p=51&code_c=51&vid=861557177515977&dv=android&os=4.4.4&rl=720*1280&ac=WIFI'

            yield scrapy.Request(headers=response.headers,url=url,meta={'info_from_index':one_news_dict},callback=self.parse_content_from_index)


    def parse_content_from_index(self,response):
        def replace_img(match):
            return img_url_dict_all[match.group(0)]

        data_meta_from_index=response.meta['info_from_index']

        datajson=json.loads(response.body)
        try:
            author_list = datajson['result']['author_list'][0]
            uid = author_list['uid']
            publish_user = author_list['name']
            publish_user_photo = author_list['head_img']
        except:
            return

        content_raw = datajson['result']['article']['ar_con']
        content_dealed = urllib.unquote(content_raw.encode('utf-8'))

        img_url_dict_all = {}
        for num, img_url_dict in enumerate(datajson['result']['photos']):
            img_url_dict_all.update(
                {
                    '[img:' + str(num) + ']': '<img src="' + str(img_url_dict['image']) + '">' + str(
                        img_url_dict['intro'].encode('utf-8')) + '</img>'
                }
            )
        content = re.sub(r'\[img\:\d{1,2}\]', replace_img, content_dealed)
        publish_time = time.strftime('%Y-%m-%d %H:%M:%S')
        data_meta_from_index['publish_time'] = publish_time
        data_meta_from_index['content'] = content
        data_meta_from_index['publish_user_id'] = uid
        data_meta_from_index['publish_user'] = publish_user
        data_meta_from_index['publish_user_photo'] = publish_user_photo

        host = 'appapi.jiemian.com'
        commenturl = 'http://' + host + '/v4/5.1.0/10001/comment/get_article_comment/' + str(
            id) + '.json?vid=861557177515977&dv=android&os=4.4.4&rl=720*1280&ac=WIFI'

        return scrapy.Request(url=commenturl,headers=response.headers,meta={'info_from_content':data_meta_from_index},callback=self.parse_comments_from_content)


    def parse(self, response):
        print 'in parse'
        print response.url


    def parse_test(self,response):
        print response.url
        print 'in test'


    def parse_comments_from_content(self,response):

        data_meta_from_content=response.meta['info_from_content']
        print response.url
        datajson=json.loads(response.body)
        for i in datajson['result']['rst']:
            id = i['id']
            content = i['content']
            like_count = i['praise']
            publish_time_stramp = str(i['published'])
            publish_user_id = i['user']['uid']
            publish_user = i['user']['nike_name']
            publish_user_photo = i['user']['head_img']
            publish_time_a = time.localtime(int(publish_time_stramp))
            publish_time = time.strftime('%Y-%m-%d %H:%M:%S', publish_time_a)
            comment_dict = {
                'id': id,
                'content': content,
                'like_count': like_count,
                # 'publish_time_stramp':publish_time_stramp,
                'publish_time': publish_time,
                'publish_user_id': publish_user_id,
                'publish_user': publish_user,
                'publish_user_photo': publish_user_photo,
                'parent_id': data_meta_from_content['id'],
                'ancestor_id': data_meta_from_content['id']
            }
            data_meta_from_content['reply_nodes'].append(comment_dict)
        # return data_meta_from_content