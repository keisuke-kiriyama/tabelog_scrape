import requests
from bs4 import BeautifulSoup
import csv
import re
import time
import pymysql.cursors


request_count = 0

class MyRequestError(Exception):
    pass

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
        error_log(err, url)
        raise MyRequestError("request timout err %s" % err)
    except requests.exceptions.TooManyRedirects as err:
        error_log(err, url)
        raise MyRequestError("request too many redirect err %s" % err)
    except requests.exceptions.RequestException as err:
        error_log(err, url)
        raise MyRequestError("request exception err %s" % err)
    except Exception as err:
        print(err)
        raise MyRequestError("request unknown err %s" % err)
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
    csv_file = open(csv_path, 'a', newline='')
    try:
        writer = csv.writer(csv_file)
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
    save_to_db(name, address, url)


def search_prefecture():
    site_map_url = 'https://tabelog.com/sitemap/'
    res = create_get_request(site_map_url)
    bs_obj = BeautifulSoup(res.text, 'lxml')
    prefectures = bs_obj.findAll('ul', {'class':'clearfix'})
    for prefecture in prefectures:
        if 'id' in prefecture.attrs:
            continue
        pre_links = prefecture.findAll('a')
        for pre_link in pre_links:
            if 'href' in pre_link.attrs:
                pre_url = site_map_url.replace('/sitemap/', pre_link.attrs['href'])
                try:
                    search_region(pre_url)
                except:
                    continue


def search_region(pre_url):
    try:
        res = create_get_request(pre_url)
        bs_obj = BeautifulSoup(res.text, 'lxml')
    except:
        return -1
    region_list = bs_obj.find('ul', {'class':'clearfix'})
    regions = region_list.findAll('a')
    for region in regions:
        if 'href' in region.attrs:
            region_url = region.attrs['href']
            try:
                search_initial(region_url)
            except:
                continue


def search_initial(region_url):
    try:
        res = create_get_request(region_url)
        bs_obj = BeautifulSoup(res.text, 'lxml')
    except:
        return -1
    tag_list = bs_obj.find('div', {'class':'taglist'})
    tags = tag_list.findAll('a')
    for tag in tags:
        if 'href' in tag.attrs:
            tag_url = tag.attrs['href']
            try:
                search_shop(tag_url)
            except:
                continue


def search_shop(tag_url):
    try:
        res = create_get_request(tag_url)
        bs_obj = BeautifulSoup(res.text, 'lxml')
    except:
        return -1
    shops = bs_obj.findAll('div', {'class':'item'})
    for shop in shops:
        shop_tag = shop.find('a')
        if 'href' in shop_tag.attrs:
            shop_url_short = shop_tag.attrs['href']
            shop_url = 'https://tabelog.com' + shop_url_short
            try:
                get_shop_data(shop_url)
            except:
                continue


def save_to_db(name, address, url):
    connection = pymysql.connect(host='localhost',
                                 user='root',
                                 db='shop_data',
                                 charset='utf8mb4',
                                 cursorclass=pymysql.cursors.DictCursor)
    try:
        with connection.cursor() as cursor:
            sql = "INSERT INTO shop_data (name, address, url) VALUES (%s, %s, %s);"
            cursor.execute(sql, (name, address, url))
        connection.commit()
    finally:
        connection.close()


def error_log(err, url):
    log_file = open('../files/error.log', 'a')
    log_file.write(url)
    log_file.write(err)
    log_file.close()


search_prefecture()
#search_region('https://tabelog.com/sitemap/tokyo/')