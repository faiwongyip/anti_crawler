# -*- coding: utf-8 -*-
import csv 
import os 
import pymssql
from scrapy.conf import settings

class FeedCsvPipeline(object):
    def process_item(self, item, spider):
        filename = os.getcwd() + '\\data\\%s_%s.csv' % (item['classify'], item['updatetime'])
        # filename = os.getcwd() + '\\data\\%s.csv' % (spider.name)
        if not os.path.exists(filename):
            with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
                f = csv.writer(csvfile)
                f.writerow(sorted(item.keys()))
        with open(filename, 'a', newline='', encoding='utf-8') as csvfile:
            f = csv.writer(csvfile)
            f.writerow([item[key] for key in sorted(item.keys())])
        # return item
        
class MssqlPipeline(object):
    def __init__(self):
        self.conn = pymssql.connect(host=settings['MSSQL_HOST_119'],database=settings['MSSQL_DB_DOWN'],user=settings['MSSQL_USER'],password=settings['MSSQL_PW_119'],charset='UTF-8')
        self.cur = self.conn.cursor()
        
    def process_item(self, item, spider):
        if item['classify'] == 'compare':
            sql = """
                    insert into compare_index(carseries1id, carseries1, carseries2, value, ranking, area, date)
                    values('%s', '%s', '%s', '%s', '%s', '%s', '%s')
                """ % (item['carseries1id'], item['carseries1'], item['carseries2'], item['index'], item['ranking'], item['area'], item['date'])
        else:
            sql = """
                    insert into attention_index(carseriesid, carseries, value, area, date)
                    values('%s', '%s', '%s', '%s', '%s')
                """ % (item['carseriesid'], item['carseries'], item['index'], item['area'], item['date'])
        self.cur.execute(sql)
        self.conn.commit()
        # return item
    
    def close_spider(self, spider):
        self.cur.close()
        self.conn.close()
                
                
                
                
                
                
                