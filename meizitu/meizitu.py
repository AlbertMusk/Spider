#encoding: utf-8

import requests
from bs4 import  BeautifulSoup
import os

# 初始化headers
headers = {
    'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.109 Safari/537.36',
}

# 获取一个bs对象
def get_soup(url, headers=headers):
    response = requests.get(url, headers=headers)
    return BeautifulSoup(response.text, 'lxml')

# 每页的爬取方法都是一样的
def get_one_page(page_number):
    # 首先获取页面中每一个图集的url
    url = 'https://www.mzitu.com/xinggan/page/' +  str(page_number)
    main_soup = get_soup(url)
    # 获取对应页中每个图集对应的url
    for url in main_soup.find(id='pins').select('li span a'):
        headers['Referer'] = url['href']
        soup = get_soup(url['href'], headers)
        title = soup.find('h2').text
        # 获取每个图集中的页数
        index = soup.find(class_='dots').find_next_sibling().string
        print('开始下载 - ' + title)
        for i in range(1, int(index)+1):
            page_url = url['href'] + '/' + str(i)
            img_soup = get_soup(page_url, headers)
            img_url = img_soup.find(class_='main-image').find('img')['src']

            img_name = title + '/' + str(i) + '.jpg'

            # 创建文件夹
            if not os.path.exists(title):
                os.makedirs(title)

            if os.path.exists(img_name):
                print('文件已存在，不重复下载')
                continue

            # 写入文件中
            with open(img_name, 'wb') as f:
                f.write(requests.get(img_url, headers=headers).content)
                f.close()
                print('Done --- 已完成-' + str(i) + '/' + index)

# 判断是否下载单一目标页


def main():
    # 获取可爬取的页数
    print(get_soup('https://www.mzitu.com/xinggan').find(class_='dots').find_next_sibling().string)

    bool = input('是否下载单一目标页， Y/N')
    if bool is 'y' or 'Y':
        page_number = input('请问要爬取的单一页数')
        get_one_page(page_number)
    if bool is 'n' or 'N':
        page_number = input('请问要爬取的页数')
        for i in range(1, int(page_number)):
            get_one_page(i)



if __name__ == '__main__':
    main()