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
    name = 'datamodel'
    
    def __init__(self):
        self.updatetime = time.strftime('%Y%m%d%H%M%S', \
                            time.localtime())
        self.cars = []
        self.dateList = []
        with open('searchCsName.txt') as f1, open('searchYears.txt') as f2:
            for row in f1:
                data = row.strip()
                self.cars.append(data)
            for row in f2:
                y = row.strip()
                for m in range(1,13):
                    y_m = y + '%02d' % m
                    self.dateList.append(y_m)
                
    def start_requests(self):
        for i,cs in enumerate(self.cars):
            print(cs)
            yield Request(
                url = 'http://datamodel.bitauto.com/findSearchName.do?searchName=' + request.quote(cs),
                callback = self.parse_findSearchName,
                meta = {
                    'cs':cs, 
                    'cookiejar':i
                } 
            )
            
    def parse_findSearchName(self, response):
        if response.text == 'success':
            yield Request(
                url = 'http://datamodel.bitauto.com/search.do?searchName=%s' % request.quote(response.meta['cs']),
                callback = self.parse_url,
                meta = {
                    'cs':response.meta['cs'], 
                    'cookiejar':response.meta['cookiejar']
                },
                headers = {
                    'Host':'datamodel.bitauto.com',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
                    'Referer':'http://datamodel.bitauto.com/'
                }
            )
        else:
            yield Request(
                url = 'http://datamodel.bitauto.com/searchName.do?searchName=' + request.quote(response.meta['cs']),
                callback = self.parse_search,
                meta = {
                    'cs':response.meta['cs'], 
                    'cookiejar':response.meta['cookiejar']
                }
            )
            
    def parse_search(self, response):
        searchNames = re.findall('name":"(.*?)"', response.text)
        print(searchNames)
        if not searchNames:
            with open('err.txt', 'a', encoding='utf-8') as f:
                f.write(response.meta['cs'] + '\n')
        for searchName in searchNames:
            yield Request(
                url = 'http://datamodel.bitauto.com/search.do?searchName=%s' % request.quote(searchName),
                callback = self.parse_url,
                meta = {
                    'cs':response.meta['cs'], 
                    'cookiejar':response.meta['cookiejar']
                },
                headers = {
                    'Host':'datamodel.bitauto.com',
                    'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
                    'Referer':'http://datamodel.bitauto.com/'
                }
            )
    
    def parse_url(self, response):
        carseriesName = response.xpath("//div[@class='compare-left']/h3/text()").extract()[0]
        serialID = response.xpath("//input[@id='serialID']/@value").extract()[0]
        
        for date in self.dateList:
            compareUrl = 'http://datamodel.bitauto.com/compare/search.do?cityID=0&serialID={}&startDate={}&endDate={}'.format(serialID, date, date)
            yield Request(
                url = compareUrl,
                callback = self.parse_campare_index,
                meta = {
                    'carseriesName': carseriesName,
                    'date': date,
                    'serialID':serialID,
                    'cookiejar':response.meta['cookiejar']
                }
            )
        attentionUrl = 'http://datamodel.bitauto.com/attentionjsp.do?cityID=0&serialID=%s&selectDate=2' % serialID
        yield Request(
            url = attentionUrl,
            callback = self.parse_attention_index,
            meta = {
                'carseriesName': carseriesName, 
                'serialID':serialID,
                'cookiejar':response.meta['cookiejar']
            }
        )
        
    def parse_campare_index(self, response):
        print('parse_campare_index:', response.url, response.status)
        carseriesName = response.meta['carseriesName']
        serialID = response.meta['serialID']
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
                datas['carseries1id'] = response.meta['serialID']
                datas['carseries1'] = carseriesName
                datas['carseries2'] = name.split('~')[0]
                datas['index'] = value['value']
                datas['ranking'] = name.split('~')[1].replace('第','').replace('名','')
                datas['classify'] = 'compare'
                yield datas
    
    def parse_attention_index(self, response):
        print('parse_attention_index:', response.url, response.status)
        serialID = response.meta['serialID']
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
            for date,d in zip(datejson, datajson['data']):
                date = date.replace('年','').replace('月','')
                datas = {}
                datas['updatetime'] = self.updatetime
                datas['area'] = '全国'
                datas['date'] = date
                datas['carseriesid'] = response.meta['serialID']
                datas['carseries'] = carseriesName
                datas['index'] = d
                datas['classify'] = 'attention'
                yield datas
        