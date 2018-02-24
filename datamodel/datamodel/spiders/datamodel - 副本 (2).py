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
    name = 'datamodel2'
    
    def __init__(self):
        self.updatetime = time.strftime('%Y%m%d%H%M%S', time.localtime())
        self.dateList = []
        for y in ['2015','2016','2017']:
            for m in range(1,13):
                y_m = y + '%02d' % m
                self.dateList.append(y_m)
                
    def start_requests(self):
        with open('findSearchName.txt',encoding='utf-8') as f:
            for i,row in enumerate(f):
                row = row.strip().split('\t')
                yield Request(
                    url = 'http://datamodel.bitauto.com/search.do?searchName=%s' % request.quote(row[-1]),
                    callback = self.parse_url,
                    meta = {'cookiejar':i},
                    headers = {
                        'Host':'datamodel.bitauto.com',
                        'User-Agent':'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:55.0) Gecko/20100101 Firefox/55.0',
                        'Referer':'http://datamodel.bitauto.com/'
                    },
                    # dont_filter = True
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
                    'serialID':serialID,
                    'date': date,
                    'cookiejar':response.meta['cookiejar']
                },
                # dont_filter = True
            )
        attentionUrl = 'http://datamodel.bitauto.com/attentionjsp.do?cityID=0&serialID=%s&selectDate=2' % serialID
        yield Request(
            url = attentionUrl,
            callback = self.parse_attention_index,
            meta = {'carseriesName': carseriesName, 'serialID':serialID, 'cookiejar':response.meta['cookiejar']},
            # dont_filter = True
        )
           
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
                datas['carseries1id'] = response.meta['serialID']
                datas['carseries1'] = carseriesName
                datas['carseries2'] = name.split('~')[0]
                datas['index'] = value['value']
                datas['ranking'] = name.split('~')[1].replace('第','').replace('名','')
                datas['classify'] = 'compare'
                yield datas
    
    def parse_attention_index(self, response):
        print('parse_attention_index:', response.url, response.status)
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
        