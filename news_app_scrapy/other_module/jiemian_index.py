#_*_coding:utf-8_*_
# from visit_page4 import get_response_and_text
from bs4 import BeautifulSoup
import json
import requests
import datetime


def get_index(index_board_list,content_queue=None): #将来再添加根据数据库爬取数据的功能。index_url_list=None
    host = 'appapi.jiemian.com'

    headers = {
        'User-Agent': 'JiemianNews/5.1.0 (android; android 4.4.4; ONEPLUS A3010)',
        'Content-Type': 'application/x-www-form-urlencoded',
        'Host': 'appapi.jiemian.com',
        'Connection': 'close'
    }

    index_url_list=[
    ('/v4/5.1.0/10001/cate/117/0/1/51/5101.json?vid=861557177515977&dv=android&os=4.4.4&rl=720*1280&ac=WIFI','117','商业'),
    ('/v4/5.1.0/10001/cate/643/0/1/51/5101.json?vid=861557177515977&dv=android&os=4.4.4&rl=720*1280&ac=WIFI','643','财经'),
    ('/v4/5.1.0/10001/cate/644/0/1/51/5101.json?vid=861557177515977&dv=android&os=4.4.4&rl=720*1280&ac=WIFI','644','新闻'),
    ('/v4/5.1.0/10001/cate/123/0/1/51/5101.json?vid=861557177515977&dv=android&os=4.4.4&rl=720*1280&ac=WIFI','123','科技'),
    ('/v4/5.1.0/10001/cate/138/0/1/51/5101.json?vid=861557177515977&dv=android&os=4.4.4&rl=720*1280&ac=WIFI','138','汽车'),
    ('/v4/5.1.0/10001/cate/121/0/1/51/5101.json?vid=861557177515977&dv=android&os=4.4.4&rl=720*1280&ac=WIFI','121','地产'),
    ('/v4/5.1.0/10001/cate/137/0/1/51/5101.json?vid=861557177515977&dv=android&os=4.4.4&rl=720*1280&ac=WIFI','137','金融'),
    ('/v4/5.1.0/10001/cate/139/0/1/51/5101.json?vid=861557177515977&dv=android&os=4.4.4&rl=720*1280&ac=WIFI','139','消费'),
    ('/v4/5.1.0/10001/cate/322/0/1/51/5101.json?vid=861557177515977&dv=android&os=4.4.4&rl=720*1280&ac=WIFI','322','证券'),
    ('/v4/5.1.0/10001/cate/183/0/1/51/5101.json?vid=861557177515977&dv=android&os=4.4.4&rl=720*1280&ac=WIFI','183','时尚'),
    ('/v4/5.1.0/10001/cate/259/0/1/51/5101.json?vid=861557177515977&dv=android&os=4.4.4&rl=720*1280&ac=WIFI','259','工业'),
    ('/v4/5.1.0/10001/cate/495/0/1/51/5101.json?vid=861557177515977&dv=android&os=4.4.4&rl=720*1280&ac=WIFI','495','数据'),
    ('/v4/5.1.0/10001/cate/505/0/1/51/5101.json?vid=861557177515977&dv=android&os=4.4.4&rl=720*1280&ac=WIFI','505','美丽中国'),
    ('/v4/5.1.0/10001/cate/181/0/1/51/5101.json?vid=861557177515977&dv=android&os=4.4.4&rl=720*1280&ac=WIFI','181','热读')
]
    for one_index_url in index_board_list:
        # url='http://'+host+one_index_url[0]
        url=one_index_url['url']
        channelId=one_index_url['channelId']
        channelName=one_index_url['channelName']

        response=requests.get(url=url,headers=headers)
        data=json.loads(response.text)
        for one_article in data['result']['list']:
            try:
                article=one_article['article']
            except:
                continue
            id= article['ar_id']  # id
            abstract=article['ar_sum']
            title =article['ar_tl']  # title
            reply_count= article['ar_cmt']  # 评论数
            read_count= article['ar_hit']  # 点击数
            url= article['ar_surl']  # url
            publish_user= article['ar_an']  # publish_user
            publicTimestamp=article['ar_pt']
            try:
                if u'w' in read_count:
                    read_count=float(str(read_count.replace(u'w','')))
                    read_count=int(read_count*1000)
            except Exception as e:
                print e
                pass
            one_news_dict={
                'id':str(id),
                'title':str(title.encode('utf-8')),
                'reply_count':reply_count,
                'read_count':read_count,
                'url':str(url),
                'publish_user':str(publish_user.encode('utf-8')),
                'channelId':str(channelId),
                'publicTimestamp':int(str(publicTimestamp)),
                'channelName':channelName,
                'abstract':str(abstract.encode('utf-8')),
                'params':None,
                'appname': 'JieMianXinWen',
                'spider_time':datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            content_queue.put(one_news_dict)