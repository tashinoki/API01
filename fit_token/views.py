from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
import json

from .webdrive import get_fit_token
from . import webdrive

from DB.mongo import NewMyfit
from module.crypto import AESCipher
from module.scrape import create_html_element

import sys
sys.path.append('../DB')
sys.path.append('../module')


'''
user_mst → user_data
stu_mst  → user_data_detail
'''


# 基底クラス
'''
FitTokenUid → user_uidからtoken
FitTokenId  → user_id, user_pwdからtoken
'''


# 両クラスのベースとなるクラス
# fit_tokenを暗号化させて保存する役目を持つ
class FitTokenBase(View):

    @staticmethod
    def encrypt_fit_token(user_uid, fit_token):

        cipher = AESCipher(user_uid)
        return cipher.encrypt(fit_token)

    # DBのtokenのセッションがまだ生きているのか確かめる
    @staticmethod
    def fetch_token_from_db(user_uid=None, user_id=None):
        """
        :param user_uid:
        :param user_id:
        :return: dbから取得した既存のfit_token
        """
        encrypted_fit_token = ''
        if user_uid:
            user_data = NewMyfit.user_mst().find_one({'user_uid': user_uid}, {'fit_token': 1, '_id': 0})
            encrypted_fit_token = user_data['fit_token']

        elif user_id:
            user_data = NewMyfit.user_mst().find_one({'user_id': user_id}, {'fit_token': 1, '_id': 0})
            encrypted_fit_token = user_data['fit_token']

        return encrypted_fit_token

    # DBの暗号化fit_tokenを複合する
    @staticmethod
    def decrypt_fit_token(user_uid, encrypted_fit_token):

        cipher = AESCipher(user_uid)
        return cipher.decrypt(encrypted_fit_token)

    @staticmethod
    def token_pre_request(fit_token):
        """
        tokenが生きているかの確認
        :param fit_token: dbから取得するトークン。セッションが生きていれば有効
        :return: True or False
               : セッションが有効か同課の判定結果のみ返す
        """

        html_element = create_html_element(fit_token=fit_token)
        return html_element.find(id='form1:logout') == None


# Create your views here.
class FitTokenUid(FitTokenBase):

    # @staticmethod
    def post(self, request):

        user_uid = request.POST['userUid']

        encrypted_fit_token = self.fetch_token_from_db(user_uid=user_uid)
        fit_token = self.decrypt_fit_token(user_uid, encrypted_fit_token).decode('utf-8')
        print('old fit_token', fit_token)
        is_token_alive = self.token_pre_request(fit_token)
        print('is token_alive', is_token_alive)

        # 既存tokenのセッションが有効な場合
        if is_token_alive:
            print('aliving token', fit_token)
            return HttpResponse(json.dumps({'fit_token': True}))

        user_data = NewMyfit.user_mst().find_one({'user_uid': user_uid}, {'user_id': 1, 'user_pwd': 1, '_id': 0})

        user_pwd = self.decrypt_user_data(user_uid, user_data['user_pwd']).decode('utf-8')
        print('user_pwd', user_pwd)
        try:
            fit_token = webdrive.get_fit_token(user_data['user_id'], user_pwd)
            print('new fit_token', fit_token)

            encrypted_fit_token = super().encrypt_fit_token(user_uid, fit_token)

            NewMyfit.user_mst().update({'user_uid': user_uid}, {'$set': {'fit_token': encrypted_fit_token}})

            return HttpResponse(json.dumps({'fit_token': True}))

        except:
            return HttpResponse(json.dumps({'fit_token': False}))

    @staticmethod
    def decrypt_user_data(user_uid, encryped_user_pwd):

        cipher = AESCipher(user_uid)
        return cipher.decrypt(encryped_user_pwd)


# user idをもとにfit tokenを取得
# 処理の関係で暗号化のtokenがdata baseに存在しない可能性もある
class FitTokenId(FitTokenBase):

    # @staticmethod
    def post(self, request):

        user_id = request.POST['userId']
        user_pwd = request.POST['userPwd']

        try:
            fit_token = get_fit_token(user_id, user_pwd)
            print(fit_token)

            user_data = NewMyfit.user_mst().find_one({'user_id': user_id}, {'user_uid': 1, '_id': 0})

            encrypted_fit_token = super().encrypt_fit_token(user_data['user_uid'], fit_token)

            NewMyfit.user_mst().update({'user_uid': user_data['user_uid']}, {'$set': {'fit_token': encrypted_fit_token}})
            return HttpResponse(json.dumps({'fit_token': True}))

        except:
            return HttpResponse(json.dumps({'fit_token': False}))
