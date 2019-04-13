import requests,os
from bs4 import BeautifulSoup as bs

headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}

path = 'U:\\book\\'

def get_proxy():
    return requests.get("http://95.179.226.235:5010/get/").text

def delete_proxy(proxy):
    requests.get("http://95.179.226.235:5010/delete/?proxy={}".format(proxy))

def download_book(isbn, url):
    while True:
        proxy = get_proxy()
        print('开始使用代理')
        try:
            html = requests.get(url, timeout=2 ,headers=headers, proxies={"http": "http://{}".format(proxy)})
            length = html.headers['content-length']
            print('content-length', length)
            if int(length) > 1024:
                print('开始下载图书')
                file_dir = path + isbn + '\\'
                if not os.path.exists(file_dir):
                    os.mkdir(file_dir)
                    print('创建文件夹成功')
                file_name = file_dir + url.split('/')[-1]
                print('正在下载:' + isbn)
                with open(file_name, 'wb') as f:
                    f.write(html.content)
                    print('done')
                    f.close()
                break
        except Exception as e:
            print(e)
            continue

def get_book_link(url):
    r = requests.get(url, headers=headers)
    if r.status_code == 200:
        soup = bs(r.text, 'lxml')
        isbn = soup.select('#mbm-book-page > div.mbm-book-details-outer > div > span:nth-child(16)')[0].text
        link_list = soup.select('#mbm-book-links1 > div > ul > li > a')
        for link in link_list:
            print('开始下载')
            download_book(isbn, link.get('href'))

def get_book():
    for page in range(1, 132):
        url = 'https://bookset.me/page/' + str(page)
        r = requests.get(url, headers=headers)
        if r.status_code == 200:
            soup = bs(r.text, 'lxml')
            cardslist = soup.find(id='cardslist')
            for card in cardslist:
                h3 = card.find('h3')
                if not isinstance(h3,int):
                    get_book_link(h3.find('a').get('href'))
        print('已完成:', page)

if __name__ == '__main__':
    get_book()