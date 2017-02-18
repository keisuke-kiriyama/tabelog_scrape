import requests
from bs4 import BeautifulSoup
import csv
import re
import sys
import time

request_count = 0

def create_get_request(url):
    global request_count
    request_count += 1
    time.sleep(3)
    print('request count : ' + str(request_count))
    session = requests.Session()
    headers = {
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_3)' 'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
        'Accept': '*/*'}
    try:
        res = session.get(url, headers=headers)
    except requests.exceptions.Timeout as err:
        print(err)
        sys.exit(1)
    except requests.exceptions.TooManyRedirects as err:
        print(err)
        sys.exit(1)
    except requests.exceptions.RequestException as err:
        print(err)
        sys.exit(1)
    return res


def get_name(bs_obj):
    name = bs_obj.find('p', {'class':'mname'}).find('strong')
    name_text = name.get_text()
    return name_text


def get_address(bs_obj):
    address = bs_obj.find('tr', {'class':'address'}).find('p', {'rel':'address'})
    address_text = address.get_text()
    address_text = re.sub(' ', '', address_text)
    return address_text


def create_csv(csv_path, name, address, url):
    csv_file = open(csv_path, 'w+', newline='')
    try:
        writer = csv.writer(csv_file)
        writer.writerow(('name', 'address', 'url'))
        writer.writerow((name, address, url))
    finally:
        csv_file.close()


def get_shop_data(url):
    res = create_get_request(url)
    bs_obj = BeautifulSoup(res.text, 'lxml')
    name = get_name(bs_obj)
    address = get_address(bs_obj)
    print(name, address, url)
    create_csv('../files/shop_data.csv', name, address, url)


def search_prefecture():
    res = create_get_request('https://tabelog.com/')
    bs_obj = BeautifulSoup(res.text, 'lxml')
    prefectures = bs_obj.findAll('li', {'class':'rsttop-search__pref-list-item'})
    for prefecture in prefectures:
        pre_url = prefecture.find('a')
        if 'href' in pre_url.attrs:
            search_shop(pre_url.attrs['href'])


def search_shop(shop_list_page_url):
    res = create_get_request(shop_list_page_url)
    bs_obj = BeautifulSoup(res.text, 'lxml')
    shop_urls = bs_obj.findAll('a', {'class':'list-rst__rst-name-target cpy-rst-name'})
    for shop_url in shop_urls:
        if 'href' in shop_url.attrs:
            get_shop_data(shop_url.attrs['href'])
    try:
        next_button = bs_obj.find('a',{'class':'page-move__target page-move__target--next'})
        if 'href' in next_button.attrs:
            next_page_url = next_button.attrs['href']
            print(next_page_url)
            search_shop(next_page_url)
    except:
        return


#get_shop_data('https://tabelog.com/aomori/A0203/A020301/2008975/')
search_prefecture()
