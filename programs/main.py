import requests
from bs4 import BeautifulSoup
import csv
import re
import sys

def create_get_request(url):
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
    print(name,address,url)
    create_csv('../files/shop_data.csv', name, address, url)

get_shop_data('https://tabelog.com/tokyo/A1314/A131405/13159567/')