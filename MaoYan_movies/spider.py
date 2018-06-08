import json
import re
import requests
from requests.exceptions import RequestException
#定义抓取一个页面代码
def get_one_page(url):
    headers={
        'User-Agent':'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.108 Safari/537.36 2345Explorer/8.7.0.16013'
    }
    #定义异常
    try:
        response=requests.get(url,headers=headers)
        #根据状态码判断是否抓取成功
        if response.status_code==200:
            return response.text
        return  None
    except RequestException:
        return  None

#解析网页
def parse_one_page(html):
    #每次要加起始符和结束符
    pattern=re.compile('<dd>.*?board-index.*?">(\d+)</i>.*?data-src="(.*?)".*?</a>.*?name"><a.*?>(.*?)</a>'
                       +'.*?star">(.*?)</p>.*?releasetime">(.*?)</p>'
                        +'.*?integer">(.*?)</i>.*?fraction">(.*?)</i>.*?</dd>',re.S)
    items=re.findall(pattern,html)
    for item in items:
        yield {
            'index':item[0],
            'image':item[1],
            'title':item[2],
            #切片，去掉'主演：'
            'actor':item[3].strip()[3:],
            'time':item[4].strip()[5:],
            'score':item[5]+item[6]
        }

#写入文件
def write_to_file(content):
    #加encoding显示中文，写入方式为'a'，否则只能写一条
    with open('result.txt','a',encoding='utf-8') as f:
        f.write(json.dumps(content,ensure_ascii=False)+'\n')
        f.close()

#根据图片链接下载图片
def download(image_url, pathname):
    headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.108 Safari/537.36 2345Explorer/8.7.0.16013'
        }
    response = requests.get(image_url, headers=headers)
    with open(pathname, 'ab') as f:
        f.write(response.content)   #二进制文件
        f.close()

#定义main方法调用
#根据网页结构加入参数offset，获得下一页内容
def main(offset):
    #把offset作为参数传入url
    url="http://maoyan.com/board/4?offset="+str(offset)
    html=get_one_page(url)
    count=0   #下载的图片计数
    for item in parse_one_page(html):
        print(item)
        #把爬取的内容写入txt文件
        write_to_file(item)
        #下载图片到文件夹
        pathname = "D:\\spider\\image\\" + str(count + 1) + ".jpg"
        download(item['image'], pathname)
        count = count + 1


if __name__=='__main__':
    #读取10页前100个电影，构造0-90的循环
    for i in range(10):
        main(i*10)
