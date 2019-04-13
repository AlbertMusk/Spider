#encoding: utf-8
import requests,re
from bs4 import BeautifulSoup as bs
from pymongo import MongoClient

# conn = MongoClient('127.0.0.1', 27017)
# db = conn.books
# my_set = db.book_link

def get_book_link():
    res = requests.get('https://salttiger.com/archives/')
    soup = bs(res.text, 'lxml')
    aslist = soup.select('.car-list li ul li a')
    for a in aslist:
        try:
            response = requests.get(a.get('href'))
            # print(response.text)
            soup = bs(response.text, 'lxml')
            name = soup.find('article').find('h1').text
            content = soup.find(class_='entry-content')
            href = content.find_all('a')[1]['href']
            text = content.find_all('p')[0].find('strong')
            # print(name + ' : ' + a + ' + ' + code)
            if text:
                result = re.search(".*?提取码.*?：(.*?)$", text.text, re.S)
                if result:
                    code = result.group(1)
                else:
                    code = 'None'
            print('正在下载{}, {}/{}'.format(name, aslist.index(a) + 1, len(aslist)))
            # my_set.insert({'name': name, 'link': href, 'code': code})
            with open('books.txt', 'a', encoding='utf-8') as f:
                f.write('《{}》 - {} - {}'.format(name, href, code))
                f.write('\n')
                f.close()
        except Exception as e:
            print(e)
            print('出错的name为{}, href={}, text={}'.format(name, href, text))
            continue

def book_classification():
    with open('books.txt', 'r', encoding='utf-8') as f:
        lines = f.readlines()
        for line in lines:
            try:
                result = re.search('.*? - (.*?) - (.*?)$', line, re.S)
                url = result.group(1)
                code = result.group(2)
                if code == 'None':
                    code = ''
                head = url[:4]
                if 'ed2k' in head:
                    with open('ed2k.txt', 'a', encoding='utf-8') as ed2k:
                        ed2k.write(url.strip())
                        ed2k.write('\n')
                        ed2k.close()
                else:
                    url = url.split('/')[2]
                    if 'baidu' in url:
                        with open('baidu.txt', 'a', encoding='utf-8') as baidu:
                            baidu.write('{} {}'.format(result.group(1), code))
                            baidu.write('\n')
                            baidu.close()
                    elif 'amazon' in url:
                        with open('amazon.txt', 'a', encoding='utf-8') as amazon:
                            amazon.write('{} {}'.format(result.group(1), code))
                            amazon.write('\n')
                            amazon.close()
                    elif '115' in url:
                        with open('115.txt', 'a', encoding='utf-8') as pan:
                            pan.write('{} {}'.format(result.group(1), code))
                            pan.write('\n')
                            pan.close()
                    else:
                        with open('other.txt', 'a', encoding='utf-8') as other:
                            other.write('{} {}'.format(result.group(1), code))
                            other.write('\n')
                            other.close()
            except Exception as e:
                print(e)
                continue



if __name__ == '__main__':
    #get_book_link()
    #print('全部下载完毕')
    #print('正在分类')
    book_classification()
    print('分类完毕')

