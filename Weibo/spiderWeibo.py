from bs4 import BeautifulSoup # 解析网页
from fake_useragent import UserAgent # 随机生成User-agent
import chardet  # 有时会遇到编码问题 需要检测网页编码
import re, urllib.request, socket, time, random, csv, json,requests
from requests import RequestException
import xlwings as xw
import pandas as pd

"""
网址：
https://m.weibo.cn/p/searchall?containerid=100103type%3D1%26q%3D%E5%B0%8F%E8%B5%A2%E5%8D%A1%E8%B4%B7
"""

url = 'https://m.weibo.cn/api/container/getIndex?containerid=100103type%3D61%26q%3D%E5%B0%8F%E8%B5%A2%E5%8D%A1%E8%B4%B7%26t%3D0&page_type=searchall'

def get_one_page(url):
    headers = {
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.108 Safari/537.36 2345Explorer/8.7.0.16013'
    }
    # 定义异常
    try:
        response = requests.get(url,headers=headers)
        # 根据状态码判断是否抓取成功
        if response.status_code == 200:

            return response.text
        return None
    except RequestException:
        return None

# 在 mblog 下'mblog': {'created_at': '07-01'，‘text’：“xxxx”
created_at = [] # 发表日期
text = [] #发表内容
source = [] # 来源

# ‘mblog’{....,'user':{  }}下的
ID = [] # 用户id
screen_name = [] # 昵称
statuses_count = [] # 发表微博数量
verified = [] # 认证
gender = [] # 性别
description = [] # 个性签名
followers_count = [] # 粉丝数
follow_count = [] # 关注数
reposts_count = []  # 转发数
comments_count = [] # 评论数
attitudes_count =  [] #点赞树


def parse_one_page(data):
    # data['data']['cards']和data['data']['cards']['card_group']  都是一个一维数组，需要得到字典
    card_group = data['data']['cards'][0]['card_group']
    #print(card_group)
    #print(len(card_group))
    for i in range(len(card_group)):
        mblog = card_group[i]['mblog']
        created_at.append(mblog['created_at'])
        comment = mblog['text']
        # 去除部分特殊字符
        label_filter = re.compile(r'</?\w+[^>]*>', re.S)
        comment = re.sub(label_filter, '', comment)
        '''
        # 匹配全部特殊字符转为空格
        pattern = re.compile('[^\u4E00-\u9FD5]+')
        comment = re.sub(pattern, ' ', string)
        '''
        text.append(comment)
        source.append(mblog['source'])
        reposts_count.append(mblog['reposts_count'])  # 转发数
        comments_count.append(mblog['comments_count'])  # 评论数
        attitudes_count.append(mblog['attitudes_count'])  # 点赞数

        user = mblog['user']
        ID.append(user['id'])  # 用户id
        screen_name.append(user['screen_name']) # 昵称
        statuses_count.append(user['statuses_count'])  # 发表微博数量
        verified.append(user['verified'])  # 认证
        gender.append(user['gender'])  # 性别
        description.append(user['description'])  # 个性签名
        followers_count.append(user['followers_count'])  # 粉丝数
        follow_count.append(user['follow_count'])  # 关注数
        print("第{}条数据已解析".format(i))

def save_to_excel():
    saveFileName = 'C:\\Users\\ms\\Desktop\\Weibo.xlsx'
    wb = xw.Book(saveFileName)
    detail_sheet = xw.Sheet("Sheet1")
    colList = ['screen_name','id','gender','verified','description','statuses_count','follow_count','followers_count',
                    'created_at','text','source','reposts_count','attitudes_count','comments_count']
    dataList = [screen_name,ID,gender,verified,description,statuses_count,follow_count,followers_count,
                            created_at,text,source,reposts_count,attitudes_count,comments_count]

    xw.Range('A1').expand('table').value =colList
    colNum = ['A','B','C','D','E','F','G','H','I','J','K','L','M','N']
    detail_sheet.range('A2').options(transpose=True).value = dataList[0]
    detail_sheet.range('B2').options(transpose=True).value = dataList[1]
    detail_sheet.range('C2').options(transpose=True).value = dataList[2]
    detail_sheet.range('D2').options(transpose=True).value = dataList[3]
    detail_sheet.range('E2').options(transpose=True).value = dataList[4]
    detail_sheet.range('F2').options(transpose=True).value = dataList[5]
    detail_sheet.range('G2').options(transpose=True).value = dataList[6]
    detail_sheet.range('H2').options(transpose=True).value = dataList[7]
    detail_sheet.range('I2').options(transpose=True).value = dataList[8]
    detail_sheet.range('J2').options(transpose=True).value = dataList[9]
    detail_sheet.range('K2').options(transpose=True).value = dataList[10]
    detail_sheet.range('L2').options(transpose=True).value = dataList[11]
    detail_sheet.range('M2').options(transpose=True).value = dataList[12]
    detail_sheet.range('N2').options(transpose=True).value = dataList[13]
    wb.save()

for i in range(1,11):
    print("------解析第{}页------".format(i))
    html = get_one_page(url+'&page='+str(i))
    data = json.loads(html,encoding='utf-8')
    parse_one_page(data)
save_to_excel()