# #encoding: utf-8

# c: 182.40.152.153
# t1: 2019-04-13-12
# t2: 12:23:51
# d: 12864c2b9e076f38c6ce47669c990ca1
# n: rs101
# p: 222222222

import time,random

# c = '182.40.152.153'
# d = '12864c2b9e076f38c6ce47669c990ca1'
# p = '222222222'
# n = 'rs101'
# now = time.time()
#
# localtime = time.localtime(now)
#
# t1 = time.strftime("%Y-%m-%d-%H", localtime)
# t2 = time.strftime("%H:%M:%S", localtime)

# print(t1)
# print(t2)

# url = 'http://h.syasn.com/h.php?c={}&t1={}&t2={}&d={}&n={}&p{}'.format(c, t1, t2, d, n, p)

import requests
from bs4 import BeautifulSoup as bs

headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
    }

# # 获取首页中的视频列表
# def get_movies_list():
#     url = 'http://m4.22c.im/'
#     res = requests.get(url, headers=headers)
#     soup = bs(res.text, 'lxml')
#     movies_list = soup.select('#ha')
#     for movie in movies_list:
#         print(movie.get('href'))

# 根据给出的id+页码的形式返回视频的id
def get_movie_id(href):
    href_list = list(href)[::-1]
    for i in href_list:
        try:
            int(i)
        except Exception:
            index = list(href).index(i)
            return href[:index+1]

# 解析首页中的视频列表
# return: total:视频的总集数
#         code:视频的代码
def get_all_movies(n):
    url = 'http://m4.22c.im/{}'.format(n)
    res = requests.get(url, headers=headers)
    soup = bs(res.text, 'lxml')
    movies = soup.select('#jb div')
    total = movies[0].select('a')[-1].text
    href = movies[0].select('a')[-1].get('href').replace('/', '')
    return {'total':total, 'code':get_movie_id(href)}


# n为视频代码
def get_movie_url(n):
    headers['Referer'] = 'http://h.syasn.com/?n={}&p=222222222'.format(n)

    # _=当前毫秒时间戳
    url = 'http://h.syasn.com/?n={}&_={}'.format(n, str(int(time.time() * 1000)))

    # 首先访问url，然后禁止重定向
    res = requests.get(url, headers, allow_redirects=False)
    # 获取response headers中的Location，即为重定向指向的地址
    # print(res.headers['Location'])
    response = requests.get(res.headers['Location'], headers=headers)
    return response.text

def get_random_str():
    return ''.join([random.choice('abcd0123456789') for x in range(10)])

def parse_url(params,n, code,random_str):
    url = ' http://dpl.syasn.com'

    url += '/{}'.format(random_str)

    for param in params.split(','):
        url += '/{}'.format(param[4:].replace("'", "").replace(';', ''))

    url += '/{}/{}.mp4'.format(code, n)

    return url

def download_movie(url, n):
    headers = {
        'Referer': 'http://m4.22c.im/{}'.format(n),
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.103 Safari/537.36',
    }
    try:
        res = requests.get(url, timeout=5, headers=headers)
        print('开始下载')
        with open(n+'.mp4', 'ab') as f:
            f.write(res.content)
            f.close()
    except Exception as e:
        print(e)
        return

def main():
    # 通过随便给出的一个id+页码 格式的代码
    # 获取该视频id的集数和id
    data = get_all_movies('4k48')
    # 返回total和id
    total = data['total']
    code = data['code']
    for i in range(1, int(total)+1):

        n = code + str(i)

        url = parse_url(get_movie_url(n),n, code, get_random_str())
        print('获取成功：{}'.format(n))
        print(url)
        # download_movie(url, n)

if __name__ == '__main__':
    main()