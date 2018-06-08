import re
from selenium import webdriver
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from pyquery import PyQuery as pq
import pymongo

browser = webdriver.Chrome ()
wait = WebDriverWait(browser, 10)

MONGO_URL = 'localhost'
MONGO_DB = 'taobao'
MONGO_TABLE = 'product'
#引入
client = pymongo.MongoClient(MONGO_URL)
db = client[MONGO_DB]

def search():
    # 定义搜索的方法
    try:
        browser.get('https://taobao.com')
        # 浏览器加载需要时间，判断浏览器加载成功后再执行操作,python-selenium官网查看waits_api
        # 设置指定时间和加载目标
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#q")))    #商品搜索框
        #搜索按钮
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#J_TSearchForm > div.search-button > button')))
        input.send_keys('美食')    #搜索框中输入参数
        submit.click()    #点击按钮
        #通过等待，审查搜索后的总页数，判断网页全部加载出来
        total = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > div.total')))
        return total.text
    except TimeoutException:
        search()

def next_page(page_number):
    # 定义翻页函数
    try:
        # 页面搜索框
        input = wait.until(EC.presence_of_element_located((By.CSS_SELECTOR, "#mainsrp-pager > div > div > div > div.form > input")))
        # 确定按钮
        submit = wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, '#mainsrp-pager > div > div > div > div.form > span.btn.J_Submit')))
        input.clear()    # 清空搜索框内容
        input.send_keys(page_number)
        submit.click()
        # 搜索框内写入的页数要跟高亮显示的按钮的字数一样
        wait.until(EC.text_to_be_present_in_element(
            (By.CSS_SELECTOR,'#mainsrp-pager > div > div > div > ul > li.item.active > span'),str(page_number)))
        #判断正确后，获得商品信息
        get_products()
    except TimeoutException:
        next_page(page_number)

def get_products():
    # 判断是否有加载的信息
    wait.until(EC.presence_of_element_located((By.CSS_SELECTOR,'#mainsrp-itemlist .items .item')))
    #获得源码
    html = browser.page_source
    #解析
    doc = pq(html)
    #items()方法可以得到所有选择的内容
    items = doc('#mainsrp-itemlist .items .item').items()
    for item in items:
        product = {
            'price': item.find('.price').text(),    #价格
            'image': item.find('.pic .img').attr('src'),    #图片
            'deal': item.find('.deal-cnt').text()[:-3],    # 成交数，去掉末尾的“人付款”
            'title': item.find('.title').text(),    #标题
            'location': item.find('.location').text(),    #地点
            'shop': item.find('.shop').text()    #店名
        }
        print(product)
        save_to_mongo(product)

def save_to_mongo(result):
    try:
        if db[MONGO_TABLE].insert(result):
            print("保存到mongodb成功",result)
    except Exception:
        print("存储到mongodb失败")

def main():
    total = search()
    #提取页数的数字
    total = int(re.compile('(\d+)').search(total).group(1))    #字符串强制转换为整数
    for i in range(1, total + 1):
        next_page(i)

if __name__ == '__main__':
    main()


