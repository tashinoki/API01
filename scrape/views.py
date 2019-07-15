

from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View

from DB.mongo import NewMyfit
from DB import rdbms

from module import scrape
from module.crypto import AESCipher

import asyncio
import time
import json
import sys
sys.path.append('../DB')
sys.path.append('../module')

"""
myfitの画面からスクレイプする

StuNoticeInfo
学生のお知らせ情報をスクレイプする

StuClassInfo
学生の授業場情報をスクレイプする
"""


class StuInfoBase(View):

    @staticmethod
    def _decrypt_fit_token(user_uid, encrypted_fit_token):
        cipher = AESCipher(user_uid)
        return cipher.decrypt(encrypted_fit_token)

    @staticmethod
    def _select_fit_token(user_uid):
        user_data = NewMyfit.user_mst().find_one({'user_uid': user_uid}, {'fit_token': 1, '_id': 0})
        return user_data['fit_token']

    # MongoDBに更新をかけてクライアントに結果を返す
    async def update_local_db(self, user_uid, notice_info_list, loop):

        await self.scrape_notice_detail(loop)

        for notice_info in reversed(notice_info_list):
            NewMyfit.stu_mst().update({
              'user_uid': user_uid
            }, {
              '$addToSet': {
                'notice_info': notice_info
              }
            })

        return HttpResponse(json.dumps({'mess': notice_info_list}))

    @staticmethod
    async def scrape_notice_detail(loop):
        print('hello')
        time.sleep(10)
        loop.stop()


class StuNoticeInfo(StuInfoBase):

    def post(self, request):
        user_uid = request.POST['userUid']
        encrypted_fit_token = self._select_fit_token(user_uid)
        fit_token = self._decrypt_fit_token(user_uid, encrypted_fit_token).decode('utf-8')
        notice_info_list = scrape.scrape_notice_info(fit_token)
        #
        # loop = asyncio.new_event_loop()
        # asyncio.set_event_loop(loop)
        # asyncio.ensure_future(self.update_local_db(user_uid, notice_info_list, loop))
        # loop.run_forever()
        """
        受信した情報を古い順に保存していく
        DBの末尾が最新のものになる
        """
        for notice_info in reversed(notice_info_list):
            NewMyfit.stu_mst().update({
              'user_uid': user_uid
            }, {'$addToSet': {
              'notice_info': notice_info
            }})

        """
        ここにMySQLの非同期処理を書く
        """
        return HttpResponse(json.dumps({'mess': notice_info_list}))


class StuClassInfo(StuInfoBase):

    def post(self, request):
        return HttpResponse(json.dumps({'mess': 'this is scrape class info'}))
