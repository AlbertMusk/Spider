
import requests
import json
from bs4 import BeautifulSoup as bs
import pymongo

client = pymongo.MongoClient(host='localhost', port=27017)

db = client['goods']

collection = db['detail']

goods_list_url = 'http://www.mypricemix.com/ajax/wap/getGoodsList'
goods_detail_url = 'http://www.mypricemix.com/ajax/wap/goods_detail'
head_url = 'http://www.mypricemix.com'

headers = {
    'Cookies': "PHPSESSID=e2rgo4s9r57l2lt4cbkbh1e641; gr_user_id=0583a967-0250-43cf-b6aa-3f250cda527f; _smt_uid=5c972271.53ed79f8; pageFrom=CATEGORY; scrollTop=0; gr_session_id_b2d50a5f57ca7641=81598f8f-6509-4535-8bf6-b5eb58e184a4; gr_session_id_b2d50a5f57ca7641_81598f8f-6509-4535-8bf6-b5eb58e184a4=true; category_brand_id=2_2_1",
    'Referer': 'http://www.mypricemix.com/wap/goods_list/2__1_2',
    'User-Agent': 'Mozilla/5.0 (Linux; Android 5.0; SM-G900P Build/LRX21T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Mobile Safari/537.36'
}

basic_data = {
    'discount_flg': '',
    'color_id': '0',
    'sortname': 'id',
}


def get_brands(url, headers):
    response = requests.get(url, headers=headers)
    # print(response.text)

    soup = bs(response.text, 'lxml')

    brands = soup.select('.goods-list a')

    brands_list = []

    for good in brands:
        url = head_url + str(good['href'])
        url = url.replace(' ', '%20')
        title = good.find('img')['title']
        brands_list.append({'title': title, 'url': url})

    return brands_list


def get_brand_goods_data(url, headers, brand):
    html = requests.get(url, headers=headers).text
    # print(html)
    soup = bs(html, 'lxml')
    all_products = soup.select('.mui-table-view li')
    data_dict_list = []
    for all_product in all_products:
        title = all_product.find('span').text
        for table in all_product.select('table'):
            sex = table.find('thead').find('td').text
            for product in table.find('tbody').select('tr td')[1:]:
                product_category = product.find('a').text
                data_src = product.find('a')['data_src']
                data_id_list = data_src.split('/')[3].split('_')
                for i in data_id_list:
                    if i is '':
                        data_id_list[data_id_list.index(i)] = '0'
                    if len(data_id_list) == 3:
                        data_id_list.append('0')
                        data_id_list.append('0')
                    if len(data_id_list) == 4:
                        data_id_list.append('0')
                data_dict_list.append({'title': str(brand) + ' ' + str(title), 'category': product_category, 'sex': sex,
                                       'data': {'brand_id': data_id_list[0], 'category_brand_id': data_id_list[1],
                                                'cid': data_id_list[2], 'sex': data_id_list[3],
                                            'new': data_id_list[4]}})
    return data_dict_list


def get_goods_list(url, headers, data):

    request_data = dict(basic_data, **data)

    response = json.loads(requests.post(url, headers=headers, data=request_data).text)

    # print(request_data)

    return response['data']['html']


def get_good_id(html):
    soup = bs(html, 'lxml')
    lis = soup.select('.goods-list')
    good_ids_list = []
    for li in lis:
        good_ids_list.append({'name': li.find(class_='name').text, 'id': li.find('a')['goodsid']})

    return good_ids_list


def get_good_detail(url, headers, id):
    html = json.loads(requests.post(url, headers=headers, data={'id': id}).text)['data']['html']

    soup = bs(html)
    try:
        image_src = \
        soup.select('body > div.xq-pic-box > div.mui-slider > div > div.mui-slider-item.bms.mui-active > a > img')[0][
            'src']
    except Exception as e:
        image_src = ''
        print(e)

    description = soup.find(class_='xq-js-box').find('table').find_all('tr')
    if len(description) == 2:
        description = description[1].find('span').text
    if len(description) == 1:
        description = ''

    try:
        updatatime = soup.find(class_='xq-hl-box').find_all('span')[1].text
    except Exception as e:
        updatatime = ''
        print(e)
    buy_links = soup.select('.hl-box')

    detail_dict = {'image': image_src, 'description': description, "updatatime": updatatime, 'countries': []}

    for buy_link in buy_links:

        if not buy_link.find('a'):
            link1 = buy_link.find('ul').find('li')
            if not link1.find('.')['data-url']:
                return None
            else:
                link = link1.find('.')['data-url']

            cos = buy_link.select('li')
            country = []
            for co in cos:

                countr = co.text
                country.append(countr)

        else:
            link = buy_link.find('a')['href']
            country = buy_link.find('ul').find('li').text
            # index = country.index('(')
            # country = country[:index]

        prices = buy_link.select('.price')

        price_list = []

        if len(prices) == 2:
            offical_price = prices[0].find('span').text
            rmb_price = prices[1].find('span').text
            price_list.append(offical_price)
            price_list.append(rmb_price)
        if len(prices) == 1:
            price_list.append(prices[0].find('span').text)

        shui = buy_link.find_all(text='不含当地消费税')

        detail_dict['countries'].append({'name': country, 'link': link, 'price': price_list, 'shui': shui})
    # pprint(detail_dict)

    return detail_dict


def get_goods_list_page_number(url, headers, data):
    response = json.loads(requests.post(url, headers=headers, data=data).text)
    return response['data']['allPage']


def main():
    brands_list = get_brands('http://www.mypricemix.com/', headers)
    for brand in brands_list:
        url = brand['url']
        title = brand['title']
        data_dict_list = get_brand_goods_data(url, headers, title)
        for data_dict in data_dict_list:
            data = data_dict['data']
            page_number = int(get_goods_list_page_number(goods_list_url, headers, data))
            for i in range(1, page_number + 1):
                data['page'] = str(i)
                html = get_goods_list(goods_list_url, headers, data)
                good_ids_lsit = get_good_id(html)
                for id in good_ids_lsit:
                    item = get_good_detail(goods_detail_url, headers, id['id'])
                    good_data = data_dict['data']
                    good_data['good_id'] = id['id']
                    good_data['good_name'] = id['name']
                    good_data['brand_name'] = data_dict['title']
                    good_data['category_name'] = data_dict['category']
                    good_data['sex'] = data_dict['sex']
                    detail = dict(item, **good_data)
                    detail.pop('page')
                    collection.insert(detail)
                    # print('存入商品   ' + id['id'] + '  成功')



if __name__ == '__main__':
    main()