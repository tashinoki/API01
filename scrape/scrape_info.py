
import requests
from bs4 import BeautifulSoup
import json
import re

from MongoDB.mongo import NewMyfit
from module.crypto import AESCipher

import sys
sys.path.append('../DB')
sys.path.append('../module')

fit_home_url = 'https://unipa-dai.fit.ac.jp/up/faces/up/po/Poa00601A.jsp'

fit_fetch = requests.session()


def get_fit_token_with_uid(user_uid):
    return NewMyfit.user_mst().find_one({'user_uid': user_uid}, {'fit_token': 1, '_id': 0})['fit_token'].decode('utf-8')


def create_header(fit_token):
    headers = {'Cookie': 'JSESSION='+fit_token}
    return headers


# fitのホーム画面をキャプチャ
def get_fit_home_element(user_id):
    fit_token = get_fit_token_with_uid(user_id)
    headers = create_header(fit_token)
    fit_home_screen = fit_fetch.get(fit_home_url, headers=headers)
    print(fit_home_screen)
    return BeautifulSoup(fit_home_screen.text, 'lxml')


def scrape_stu_class_info(user_uid):
    fit_home_element = get_fit_home_element(user_uid)


def scrap_stu_notice_info(user_uid):
    fit_home_element = get_fit_home_element(user_uid)
    print(fit_home_element)


if __name__ == '__main__':
    scrap_stu_notice_info('6dda861def85490468cd9e5d1409916e6104817d34102001c4c08fd8c97c52f0')
