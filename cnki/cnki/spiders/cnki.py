# -*- coding:utf-8 -*-

import datetime
import scrapy 
from urllib import request
from scrapy.http import Request
from scrapy.conf import settings
import re 

class Cnki(scrapy.Spider):
    '''每页50篇文献'''
    
    name = 'cnki'
    
    def __init__(self):
        self.updatetime = datetime.datetime.now().strftime('%Y%m%d%H%M%S')
        # self.souce_keyword = settings['SOURCE_KEYWORD']
        # self.years = settings['YEARS']
        print('\n','-'*5,'设置参数','-'*5,'\n')
        tmp_souce_keyword = input('文献来源（多个词用空格分开）：')
        tmp_years = input('年份（多个年份用空格分开）：')
        self.souce_keyword = tmp_souce_keyword.split()
        self.years = tmp_years.split()
        
    def start_requests(self):
        for i,kw in enumerate(self.souce_keyword):
            url = 'http://kns.cnki.net/kns/request/SearchHandler.ashx?action=&NaviCode=*&ua=1.11&formDefaultResult=&PageName=ASP.brief_default_result_aspx&DbPrefix=SCDB&DbCatalog=%e4%b8%ad%e5%9b%bd%e5%ad%a6%e6%9c%af%e6%96%87%e7%8c%ae%e7%bd%91%e7%bb%9c%e5%87%ba%e7%89%88%e6%80%bb%e5%ba%93&ConfigFile=SCDBINDEX.xml&db_opt=CJFQ%2CCJRF%2CCDFD%2CCMFD%2CCPFD%2CIPFD%2CCCND%2CCCJD&txt_1_sel=LY%24%25%3D%7C&txt_1_value1={}&txt_1_special1=%25&his=0&parentdb=SCDB'.format(request.quote(kw))
            yield Request(
                url = url,
                callback = self.parse_group,
                meta={'cookiejar': i},
                dont_filter = True,
            )
        
    def parse_group(self, response):
        # print('parse_search', response.url, response.status)
        url = 'http://kns.cnki.net/kns/group/doGroupLeft.aspx?action=1&Param=ASP.brief_default_result_aspx%23SCDB/%u53D1%u8868%u5E74%u5EA6/%u5E74%2Ccount%28*%29/%u5E74/%28%u5E74%2C%27date%27%29%23%u5E74%24desc/1000000%24/-/40/40000/ButtonView&cid=0&clayer=0'
        yield Request(
            url = url,
            callback = self.parse_page,
            meta={'cookiejar': response.meta['cookiejar']},
            dont_filter = True,
        )
        
    def parse_page(self, response):
        # print('parse_page', response.url, response.status)
        for year in self.years:
            url = 'http://kns.cnki.net/kns/brief/brief.aspx?dest=%E5%88%86%E7%BB%84%EF%BC%9A%E5%8F%91%E8%A1%A8%E5%B9%B4%E5%BA%A6%20%E6%98%AF%20{0}&action=5&dbPrefix=SCDB&PageName=ASP.brief_default_result_aspx&Param=%e5%b9%b4+%3d+%27{0}%27&SortType=%e5%b9%b4&ShowHistory=1&recordsperpage=50'.format(request.quote(year))
            yield Request(
                url = url,
                callback=self.parse_list,
                meta = {'cookiejar':response.meta['cookiejar']},
                dont_filter = True,
            )
            
    def parse_list(self, response):
        print('parse_list', response.url, response.status)
        
        for tr in response.xpath("//table[@class='GridTableContent']//tr[not (contains(@class,'GTContentTitle'))]"):
            datas = {}
            datas['updatetime'] = self.updatetime
            datas['title'] = tr.xpath(".//a[@class='fz14']/text()").extract()[0]
            datas['url'] = response.urljoin(tr.xpath(".//a[@class='fz14']/@href").extract()[0])
            datas['author'] = ';'.join(tr.xpath(".//td[@class='author_flag']/a/text()").extract())
            datas['source'] = ''.join(tr.xpath(".//td[contains(.//font/@class,'Mark')]//text()").extract()).strip()
            datas['datetime'] = tr.xpath(".//td[5]/text()").extract()[0].strip()
            datas['quote'] = ''.join(tr.xpath(".//td[7]//text()").extract()).strip()
            datas['download'] = ''.join(tr.xpath(".//span[@class='downloadCount']//text()").extract())
            yield Request(
                url = datas['url'],
                callback = self.parse_detail,
                meta = {'datas':datas}
            )
        if response.xpath("//a[contains(text(),'下一页')]"):
            yield Request(
                url = response.urljoin(response.xpath("//a[contains(text(),'下一页')]/@href").extract()[0]),
                callback=self.parse_list,
                meta = {'cookiejar':response.meta['cookiejar']},
                dont_filter = True,
            )
            
    def parse_detail(self, response):
        # print('parse_detail', response.url, response.status)
        datas = response.meta['datas']
        datas['summery'] = response.xpath("//span[@id='ChDivSummary']/text()").extract()[0]
        datas['keyword'] = re.sub('\s+','',''.join(response.xpath("//p[contains(label/text(),'关键词')]/a/text()").extract()))
        # print(datas)
        yield(datas)
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        
        