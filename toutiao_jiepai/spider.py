import json
from urllib.parse import urlencode
from pathlib import Path
import re
from multiprocessing import Pool
import os
from hashlib import md5
from bs4 import BeautifulSoup
from requests.exceptions import RequestException
import requests
from config import *
import pymongo

#声明mongodb数据库对象
client=pymongo.MongoClient(MONGO_URL)
db=client[MONGO_DB]

#定义索引页，请求索引页数据
def get_page_index(offset,keyword):
    #把请求的参数写入data,写成字典格式
    data={
        'offset':offset,
        'format':'json',
        'keyword':keyword,
        'autoload':'true',
        'count':'20',
        'cur_tab':3
    }
    #构造完整的请求url，urlencode可以把字典转换为url请求参数
    url='https://www.toutiao.com/search_content/?'+urlencode(data)
    # 处理requests的异常
    try:
        #利用requests请求url
        response=requests.get(url)
        #根据状态码判断返回是否成功
        if response.status_code==200:
            return response.text
        return None
    except RequestException:
        print("请求索引页出错")
        return None

#解析索引页数据
def parse_page_index(html):
    #html是字符串格式，通过json.load转化为json对象
    data=json.loads(html)
    #判断json含有data属性，然后遍历提取每个标题的url
    if data and 'data' in data.keys():    #data所有的键名
        for item in data.get('data'):
            yield item.get('article_url')

#定义详情页，请求详情页数据
def get_page_detail(url):
    # 处理requests的异常
    try:
        # 利用requests请求url
        response = requests.get(url)
        # 根据状态码判断返回是否成功
        if response.status_code == 200:
            return response.text
        return None
    except RequestException:
        print("请求详情页出错",url)
        return None

#解析详情页数据
def parse_page_detail(html,url):
    soup = BeautifulSoup(html,'lxml')
    #用select选择器选择title下的文本
    title=soup.select('title')[0].get_text()
    print(title)
    #正则表达式解析详情页面下的image_url，在json文件中
    images_pattern=re.compile('gallery: JSON.parse[(]"(.*?)"[)],\n',re.S)
    result=re.search(images_pattern,html)
    if result:
        #得到的是字符串，转化为json对象，提取url
        # 解析出来的json格式有问题，有许多多余的'\',replace去掉反斜杠’\‘
        result=str(result.group(1).replace('\\',''))
        data = json.loads(result)
        if data and 'sub_images' in data.keys():
            sub_images=data.get('sub_images')
            images=[item.get('url') for item in sub_images]
            root_dir = create_dir('D:\spider\jiepai')  # 保存图片的根目录
            download_dir = create_dir(root_dir / title)  # 根据每组图片的title标题名创建目录
            for image in images:
                download_image(download_dir, image)    #下载所有的图片
            return {
                'title':title,
                'url':url,
                'images':images
            }

#声明存入数据库
def save_to_mongo(result):
    if db[MONGO_TABLE].insert(result):
        print("存储到mongodb成功",result)
        return True
    return False

#下载图片
def download_image(save_dir,url):
    print("正在下载：",url)
    try:
        response = requests.get(url)
        if response.status_code == 200:
            #调用存储图片函数，返回二进制
            save_image(save_dir,response.content)
        return None
    except RequestException:
        print("请求图片出错",url)
        return None

def create_dir(name):
    #根据传入的目录名创建一个目录，这里用到了 python3.4 引入的 pathlib 库。
    directory = Path(name)
    if not directory.exists():
        directory.mkdir()
    return directory

#存储图片,二进制
def save_image(save_dir,content):
    '''把文件保存到本地，文件有三部分内容(路径)/（文件名）.（后缀）
    用format构造字符串(项目路径，文件名，格式),md5文件名可以避免重复'''
    #os.getcwd()程序同目录
    #file_path='{0}/{1}.{2}'.format(os.getcwd(),md5(content).hexdigest(),'jpg')
    file_path = '{0}/{1}.{2}'.format(save_dir, md5(content).hexdigest(), 'jpg')
    #如果文件不存在，开始存入
    if not os.path.exists(file_path):
        with open(file_path,'wb') as f:
            f.write(content)
            f.close()

#main方法调用
def main(offset):
    html=get_page_index(offset,'街拍')
    #遍历解析的url
    for url in parse_page_index(html):
        html=get_page_detail(url)
        if html:
            result = parse_page_detail(html,url)
            save_to_mongo(result)

#调用main方法
if __name__ == '__main__':
    groups =  [x*20 for x in range(GROUP_START,GROUP_END+1)]
    #多进程
    pool=Pool()
    pool.map(main,groups)

