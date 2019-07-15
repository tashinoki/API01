from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from ldap3 import Server, Connection
from django.middleware import csrf
# 認証の成功パターン

# server = Server('ldap://ldap01.bene.fit.ac.jp',port=389, use_ssl=True)
# conn = Connection(server, user='uid=mam19103,ou=FIT_Users,dc=bene,dc=fit,dc=ac,dc=jp', password='jy43-TJV', check_names=True, read_only=True, auto_bind=True)

# dict object を json に変換する
import json
import base64

# mongo DB 関連module
from DB.mongo import NewMyfit
from module.crypto import AESCipher

# consolenにダンプする関数
import pprint

# MongoDbのCursorオブジェクトをJsonへと変換する
from bson.json_util import dumps

# セキュリティ関連
import django.contrib.auth.hashers as hash
from django.utils.crypto import pbkdf2
import hashlib
from django.contrib.sessions.middleware import SessionMiddleware

import sys
sys.path.append('../DB')
sys.path.append('../module')

# ユーザ認証用サーバ
LDAP_SERVER_NAME = 'ldap://ldap01.bene.fit.ac.jp'
LDAP_SERVER_PORT = 389


class XsrfTokenIssue(View):

    def get(self, request):
        csrf_token = csrf.get_token(request)
        print(csrf_token)

        # NewMyfit.user_mst().update({'user_uid': '6dda861def85490468cd9e5d1409916e6104817d34102001c4c08fd8c97c52f0'}, {
        #   '$set': {'notice_info': []}
        # })

        response = HttpResponse()
        # csrf対策cookie
        # only http,expireの設定
        response.set_cookie('csrftoken', value=csrf_token)
        response["Access-Control-Allow-Origin"] = "localhost:4200"
        response['Access-Control-Allow-Credentials'] = 'true'
        response['Access-Control-Allow-Headers'] = "Content-Type, Accept, X-CSRFToken"
        response['Access-Control-Allow-Methods'] = "POST, OPTIONS"
        return response


# ログイン認証
# 認証成功 → return True
# 認証失敗 → return False
class LoginAuth(View):

    def post(self, request):
        # csrf_token = csrf.get_token(request)

        print('main login', request.COOKIES)

        user_id = request.POST['user_id']
        user_pwd = request.POST['user_password']

        request.session['user_id'] = user_id

        server = self.get_ldap_server(LDAP_SERVER_NAME, LDAP_SERVER_PORT)

        # サーバの生存確認
        if not server.check_availability():
            print('server did not exist')
            return None

        user = 'uid=%s,ou=FIT_Users,dc=bene,dc=fit,dc=ac,dc=jp' % user_id

        try:
            conn = self.set_ldap_connection(server, user, user_pwd)
        except:
            return None

        user_uid = NewMyfit.user_mst().find_one({'user_id': user_id}, {'user_uid': 1, '_id': 0})

        # ユーザがすでに登録されている
        if(user_uid):

            # request.session.create()
            # request.session['user_uid'] = user_uid['user_uid']
            # print(request.session.session_key)

            response = HttpResponse(json.dumps({
              'authRes': True,
              'session': {
                'userUid': user_uid['user_uid'],
                'userGrade': 0,
                'userClass': 0
              }
            }))
            # response.set_cookie('csrftoken', csrf_token)
            # print(response)
            # response["Access-Control-Allow-Origin"] = "localhost:4200"
            # response['Access-Control-Allow-Credentials'] = 'true'
            # response['Access-Control-Allow-Headers'] = "Content-Type, Accept, X-CSRFToken"
            # response['Access-Control-Allow-Methods'] = "POST, OPTIONS"
            return response

        # uuidの作成
        user_uid = self.create_user_uid(user_id, user_pwd)
        self.encrypt_user_data(user_uid, user_pwd)
        self.create_stu_mst(user_uid)

        return HttpResponse(json.dumps({
          'authRes': True,
          'session': {
            'userUid': user_uid,
            'userGrade': 0,
            'userClass': 0
          }
        }))

    # 認証サーバ設定
    @staticmethod
    def get_ldap_server(host="", port=389):
        return Server(host, port=port, use_ssl=True)

    # 認証サーバ接続
    @staticmethod
    def set_ldap_connection(server, user, password):
        return Connection(server, user, password, check_names=True, read_only=True, auto_bind=True)

    @staticmethod
    def create_user_uid(user_id, user_pwd):
        # uuidの作成
        user_uid = hashlib.sha256(user_id.encode() + user_pwd.encode()).hexdigest()

        NewMyfit.user_mst().insert({
          'user_uid': user_uid,
          'user_id': user_id
        })
        return user_uid

    @staticmethod
    def encrypt_user_data(user_uid, user_pwd):

        # キーの設定
        cipher = AESCipher(user_uid)

        encrypted_user_pwd = cipher.encrypt(user_pwd)

        NewMyfit.user_mst().update({'user_uid': user_uid}, {'$set': {'user_pwd': encrypted_user_pwd}})

        return

    @staticmethod
    def create_stu_mst(user_uid):
        NewMyfit.stu_mst().remove({'user_uid': user_uid})
        NewMyfit.stu_mst().insert({'user_uid': user_uid})
        NewMyfit.stu_mst().update({'user_uid': user_uid}, {
          '$set': {
            'notice_info': [], 'class_info': []
          }
        })


# 自動ユーザに認証
class AutoLogin(View):

    @staticmethod
    def post(request):

        print('auto login', request.COOKIES)
        user_uid = request.POST['userUid']

        user_data = NewMyfit.user_mst().find_one({'user_uid': user_uid}, {'user_uid': 1, '_id': 0})

        if user_data:
            user_info = NewMyfit.stu_mst().find_one({
              'user_uid': user_data['user_uid']
            }, {
              'user_uid': 1, 'user_class': 1, 'user_grade': 1, '_id': 0
            })

            return HttpResponse(json.dumps({
              'authRes': True,
              'session': {
                'userUid': user_info['user_uid'],
                'userGrade': user_info['user_grade'],
                'userClass': user_info['user_class']
              }
            }))

        return HttpResponse(json.dumps({'authRes': False}))


# 時間割の表示
class TimeTable(View):

    @staticmethod
    def get(request):

        user_uid = request.GET.get('userUid')
        print('time_table', user_uid)
        time_table = NewMyfit.stu_mst().find_one({'user_uid': user_uid}, {'pro_time_table': 1, 'pro_credit_num': 1, '_id': 0})
        # pprint.pprint(time_table['pro_time_table'])
        return HttpResponse(json.dumps({'timeTable': time_table['pro_time_table'], 'creditNum': time_table['pro_credit_num']}))
