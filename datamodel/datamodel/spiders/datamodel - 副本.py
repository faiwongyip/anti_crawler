# -*- coding:utf-8 -*-
import json
import pymssql
import re
import time
import scrapy
from datetime import datetime,timedelta
from urllib import request
from scrapy import Request
from scrapy.conf import settings

class Datamodel(scrapy.Spider):
    name = 'datamodel1'
    
    def __init__(self):
        self.updatetime = time.strftime('%Y%m%d%H%M%S', time.localtime())
        self.conn = pymssql.connect(host=settings['MSSQL_HOST'],database=settings['MSSQL_DB_DOWN'],user=settings['MSSQL_USER'],password=settings['MSSQL_PW'],charset='UTF-8')
        self.cur = self.conn.cursor()
        self.cur.execute("select distinct std_manufacture,std_carsseriesname ,carsseriesid from down.dbo.down_carsseries_mapp where srcsys='BI'")
        self.cars = self.cur.fetchall()
        self.dateList = []
        for y in ['2015','2016','2017']:
            for m in range(1,13):
                y_m = y + '%02d' % m
                self.dateList.append(y_m)
                
    def start_requests(self):
        # for i,(mf,cs,csid) in enumerate(self.cars[:1]):
            # print(mf,cs)
            # yield Request(
                # url = 'http://datamodel.bitauto.com/searchName.do?searchName=' + request.quote(cs),
                # callback = self.parse_search,
                # meta = {'mf':mf, 'cs':cs, 'csid':csid, 'cookiejar':i} 
            # )
        print(len(self.cars))
        for i,(mf,cs,csid) in enumerate(self.cars):
            print(mf,cs)
            yield Request(
                url = 'http://datamodel.bitauto.com/findSearchName.do?searchName=' + request.quote(cs),
                callback = self.parse_findSearchName,
                meta = {'mf':mf, 'cs':cs, 'csid':csid, 'cookiejar':i},
                dont_filter = True
            )
            
    def parse_findSearchName(self, response):
        if response.text == 'success':
            with open('findSearchName.txt', 'a',encoding='utf-8') as f:
                f.write('%s\t%s\t%s\t%s\n' % (response.meta['mf'],response.meta['cs'],response.meta['csid'],response.meta['cs']))
            # yield Request(
                # url = 'http://datamodel.bitauto.com/search.do?searchName=%s' % request.quote(response.meta['cs']),
                # callback = self.parse_url,
                # meta = {'mf':response.meta['mf'], 'cs':response.meta['cs'], 'csid':response.meta['csid'], 'cookiejar':response.meta['cookiejar']},
                # headers = {
                    # 'Host':'datamodel.bitauto.com',
                    # 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
                    # 'Referer':'http://datamodel.bitauto.com/'
                # }
            # )
        else:
            yield Request(
                url = 'http://datamodel.bitauto.com/searchName.do?searchName=' + request.quote(response.meta['cs']),
                callback = self.parse_search,
                meta = {'mf':response.meta['mf'], 'cs':response.meta['cs'], 'csid':response.meta['csid'], 'cookiejar':response.meta['cookiejar']},
                dont_filter = True
            )
            
    def parse_search(self, response):
        searchNames = re.findall('name":"(.*?)"', response.text)
        print(searchNames)
        if not searchNames:
            with open('err1.txt', 'a', encoding='utf-8') as f:
                f.write('%s\t%s\t%s\t%s\n' % (response.meta['mf'],response.meta['cs'],response.meta['csid'],response.meta['cs']))
        with open('findSearchName.txt', 'a', encoding='utf-8') as f:
            f.write('%s\t%s\t%s\t%s\n' % (response.meta['mf'],response.meta['cs'],response.meta['csid'],str(searchNames)))
        # for searchName in searchNames:
            # yield Request(
                # url = 'http://datamodel.bitauto.com/search.do?searchName=%s' % request.quote(searchName),
                # callback = self.parse_url,
                # meta = {'mf':response.meta['mf'], 'cs':response.meta['cs'], 'csid':response.meta['csid'], 'cookiejar':response.meta['cookiejar']},
                # headers = {
                    # 'Host':'datamodel.bitauto.com',
                    # 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
                    # 'Referer':'http://datamodel.bitauto.com/'
                # }
            # )
    
    
    def parse_url(self, response):
        # mf, cs, csid = response.meta['mf'], response.meta['cs'], response.meta['csid']
        carseriesName = response.xpath("//div[@class='compare-left']/h3/text()").extract()[0]
        serialID = response.xpath("//input[@id='serialID']/@value").extract()[0]
        
        for date in self.dateList[:15]:
            compareUrl = 'http://datamodel.bitauto.com/compare/search.do?cityID=0&serialID={}&startDate={}&endDate={}'.format(serialID, date, date)
            yield Request(
                url = compareUrl,
                callback = self.parse_campare_index,
                meta = {
                    'carseriesName': carseriesName,
                    'date': date,
                    'cookiejar':response.meta['cookiejar']
                }
            )
        attentionUrl = 'http://datamodel.bitauto.com/attentionjsp.do?cityID=0&serialID=%s&selectDate=2' % serialID
        yield Request(
            url = attentionUrl,
            callback = self.parse_attention_index,
            meta = {'carseriesName': carseriesName, 'cookiejar':response.meta['cookiejar']}
        )
            
        # kw = '速腾'
        # yield Request(
            # url = 'http://datamodel.bitauto.com/search.do?searchName=%s' % request.quote(kw),
            # callback = self.parse_search,
            # meta = {'kw': kw},
            # headers = {
                # 'Host':'datamodel.bitauto.com',
                # 'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
                # 'Referer':'http://datamodel.bitauto.com/'
            # }
        # )
        
    # def parse_search(self, response):
        # print('parse_search:', response.url, response.status)
        # kw = response.meta['kw']
        # carseriesName = response.xpath("//div[@class='compare-left']/h3/text()").extract()[0]
        # serialID = response.xpath("//input[@id='serialID']/@value").extract()[0]
        # for date in self.dateList:
            # url = 'http://datamodel.bitauto.com/compare/search.do?cityID=0&serialID={}&startDate={}&endDate={}'.format(serialID, date, date)
            # yield Request(
                # url = url,
                # callback = self.parse_campare_index,
                # meta = {
                    # 'kw': kw,
                    # 'carseriesName': carseriesName,
                    # 'date': date,
                # }
            # )
        # # campareValueID = response.xpath("//input[contains(@id,'compare_valueid')]/@value").extract()
        # # campareValueID.insert(0,serialID)
        # url = 'http://datamodel.bitauto.com/attentionjsp.do?cityID=0&serialID=%s&selectDate=2' % serialID
        # yield Request(
            # url = url,
            # callback = self.parse_attention_index,
            # meta = {
                # 'kw': kw,
                # 'carseriesName': carseriesName,
            # }
        # )
        
    def parse_campare_index(self, response):
        print('parse_campare_index:', response.url, response.status)
        carseriesName = response.meta['carseriesName']
        date = response.meta['date']
        try:
            varName = re.findall("var name\s?=\s?'(\[.*?\])';", response.text)[0]
            varValue = re.findall("var value\s?=\s?'(\[.*?\])';", response.text)[0]
        except Exception as e:
            print('出错！')
            print(e)
        else:
            varName, varValue = json.loads(varName), json.loads(varValue)
            for name,value in zip(varName, varValue):
                datas = {}
                datas['updatetime'] = self.updatetime
                datas['area'] = '全国'
                datas['date'] = date
                datas['carseries1'] = carseriesName
                datas['carseries2'] = name.split('~')[0]
                datas['index'] = value['value']
                datas['ranking'] = name.split('~')[1].replace('第','').replace('名','')
                datas['classify'] = 'compare'
                yield datas
    
    def parse_attention_index(self, response):
        print('parse_attention_index:', response.url, response.status)
        # with open('test.html','w',encoding='utf-8') as f:
            # f.write(response.text)
        
        try:
            mapStr = re.findall("var jsonSerialMapStr\s?=\s?'\[(\{.*?\})\]';", response.text)[0]
            dataStr = re.findall("var attentiondataStr\s?=\s?'\[(\{.*?\})\]';", response.text)[0]
            dateStr = re.findall("var attentiondatestr\s?=\s?'(.*?)';", response.text)[0]
        except Exception as e:
            print('出错！')
            print(e)
        else:
            mapjson, datajson, datejson= json.loads(mapStr), json.loads(dataStr), dateStr.split(',')
            tempName = datajson['name']
            name = mapjson[tempName]
            carseriesName = name
            # carseriesName = response.meta['carseriesName']
            # if name == carseriesName:
            for date,d in zip(datejson, datajson['data']):
                date = date.replace('年','').replace('月','')
                datas = {}
                datas['updatetime'] = self.updatetime
                datas['area'] = '全国'
                datas['date'] = date
                datas['carseries'] = carseriesName
                datas['index'] = d
                datas['classify'] = 'attention'
                yield datas
        