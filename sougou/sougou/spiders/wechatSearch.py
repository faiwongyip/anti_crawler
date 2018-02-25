# -*- coding:utf-8 -*-

import datetime
import re
import scrapy
from urllib import request
from scrapy import Request
from scrapy.conf import settings
from time import strftime,strptime

class Sougou(scrapy.Spider):
    '''
    搜狗搜索关键词，限定公众号，时间段推送的微信文章，保存为csv格式，文件夹在项目的data文件夹，延时1秒！
    '''
    name = 'wechatSearch'
    download_delay = 1
    
    def __init__(self,ft=None,et=None):
        self.updatetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        self.headers = {
            'Host': 'weixin.sogou.com',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Accept-Encoding': 'gzip, deflate',
            'Referer': 'http://weixin.sogou.com/weixin',
            'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
        }
        self.cookies = {'SUV':'1510560148928294','SNUID':'0F08576716134AF19D2847E617FC4212'}
        self.ft = strftime('%Y-%m-%d', strptime(ft, '%Y%m%d'))  #settings['FIRST_DATE']
        self.et = strftime('%Y-%m-%d', strptime(et, '%Y%m%d'))  #settings['END_DATE']
        # self.ft = '2016-11-15'
        # self.et = '2016-11-27'
        
    def start_requests(self):
        for line in open('user_id.txt'):
            line = line.strip().split()
            yield Request(
                url = 'http://weixin.sogou.com/weixin?type=2&ie=utf8&query={}&tsn=5&ft={}&et={}&interation=&wxid={}&usip={}'.format(request.quote(line[0]),self.ft,self.et,line[2],line[1]),
                callback = self.parse_list,
                meta = {'line': line,},
                headers = self.headers,
                cookies = self.cookies,
            )
            
    def parse_list(self, response):
        print('parse_list:', response.url, response.status)
        line = response.meta['line']
        # print('发现%s篇文章' % len(response.xpath("//ul[@class='news-list']/li")))
        for li in response.xpath("//ul[@class='news-list']/li"):
            postUrl = li.xpath(".//h3/a/@href").extract()[0]
            yield Request(
                url = postUrl,
                callback = self.parse_content,
                meta = {'line':line, },
            )
        if response.xpath("//a[@id='sogou_next']"):
            yield Request(
                url = response.urljoin(response.xpath("//a[@id='sogou_next']/@href").extract()[0]),
                callback = self.parse_list,
                meta = {'line': line, },
                headers = self.headers,
                cookies = self.cookies,
            )
        
    def parse_content(self, response):
        # print('parse_list:', response.url, response.status)
        line = response.meta['line']
        datas = {}
        datas['updatetime'] = self.updatetime
        datas['name'] = response.xpath("//a[@id='post-user']/text()").extract()[0]
        datas['user_id'] = line[1]
        datas['post_url'] = response.url
        datas['title'] = response.xpath("//h2[@id='activity-name']/text()").extract()[0].strip()
        datas['postdate'] = response.xpath("//em[@id='post-date']/text()").extract()[0]
        datas['content'] = re.sub('\s+','',''.join(response.xpath("//div[@id='js_content']//text()").extract()))
        yield datas
        
        
        
        
        
        
        
        
        
        
        