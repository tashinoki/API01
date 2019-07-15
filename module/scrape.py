
import requests
from bs4 import BeautifulSoup
import re
from lxml import etree
from .crypto import AESCipher
from DB.mongo import NewMyfit

import sys
sys.path.append('../DB')

"""
スクレイピング対象URLセット
"""
fit_main_page = 'https://unipa-dai.fit.ac.jp/up/faces/up/po/Poa00601A.jsp'


# 対象のurlからオブジェクトをとってきて
# BeautifulSoup型のHTMLエレメントに変換
def create_html_element(url='https://unipa-dai.fit.ac.jp/up/faces/up/po/Poa00601A.jsp', fit_token=None):
    request = requests.session()
    headers = {'Cookie': 'JSESSIONID=' + fit_token}
    response = request.get(url, headers=headers)
    print(response.text)
    # extract_text_from_table(response)
    return BeautifulSoup(response.text, 'lxml')


def scrape_notice_info(fit_token):
    notice_info_list = []
    notice_info = {}

    html_element = create_html_element(fit_token=fit_token)
    is_all_display = html_element.find(id='form1:Poa00201A:htmlParentTable:1:htmlDisplayOfAll')

    """
    表示イベントが6件以上ある場合の条件分岐
    """
    # if(is_all_display):
    #     print('test')
    #     all_display_evnet = html_element.fint(id='form1:Poa00201A:htmlParentTable:1:htmlDisplayOfAll:0:allInfoLinkCommand')
    #     text = is_all_display.text
    #     pass

    # else:
    table = html_element.find(id='form1:Poa00201A:htmlParentTable:1:htmlDetailTbl')
    trs = table.find_all('tr')

    for tr in trs:
        read = tr.select_one('td.read')
        important = tr.select_one('td.important')
        title = tr.select_one('td.title')

        if title.select_one('a') is None:
            break

        notice_info['title'] = title.select_one('a').text
        notice_info['read'] = read.select_one('img') is not None
        notice_info['important'] = important.select_one('img') is not None
        notice_info['sender'] = re.sub('\xa0', '', title.select_one('span.from').text)
        notice_info['date'] = re.sub('\xa0', '', title.select_one('span.insDate').text)
        notice_info['delete'] = False

        notice_info_list.append(notice_info)
        notice_info = {}

    return notice_info_list


"""
MyFitは<table>を使ってデザインを整えている
そこをうまく利用すれば、効率的にできるのでは？

また、通知が6件以上の場合は
一覧表示のページを表伊ｚする必要がある

<table row>はかなり続くので
<innerText>がNULLになるまでforを使う
"""


def extract_text_from_table(table):
    # trs = table.find_all('td', )
    pass


def extract_attend_info(fit_token, value):

    request = requests.session()

    headers = {'Cookie': 'JSESSIONID=' + fit_token}
    print('headers', headers)

    params = {
      'header:form1:htmlMenuItemButton': '実行',
      'header:form1:hiddenMenuNo': 203,
      'header:form1:hiddenFuncRowId': 0,
      'com.sun.faces.VIEW': value,
      'header:form1': 'header:form1'
    }

    response = request.get(fit_main_page, headers=headers, params=params)
    # print(response)
    # print(response.text)
    # print(headers)
    soup = BeautifulSoup(response.text, 'lxml')

    attend_info = soup.find_all(attrs={'class': 'listTable'})[1]


def extract_sun_faces_view(html_element):
    # print(html_element)

    value = html_element.find(id='com.sun.faces.VIEW')['value']
    return value


def uid_to_token(user_uid):
    print(user_uid)
    user_data = NewMyfit.user_mst().find_one({'user_uid': user_uid}, {'fit_token': 1, '_id': 0})

    cipher = AESCipher(user_uid)
    fit_token = cipher.decrypt(user_data['fit_token']).decode('utf-8')
    return fit_token
