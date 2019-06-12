from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View

# dict object を json に変換する
import json
import base64

# 親ディレクトリを追加する
import sys
sys.path.append('../MongoDB')

# mongo DB 関連module
from MongoDB.mongo import NewMyfit

# consolenにダンプする関数
import pprint

# MongoDbのCursorオブジェクトをJsonへと変換する
from bson.json_util import dumps

# セキュリティ関連
import django.contrib.auth.hashers as hash
from django.utils.crypto import pbkdf2
import hashlib


# ログイン認証
# 認証成功 → return True
# 認証失敗 → return False
class LoginAuth(View):

  def post(self, request):
    posted_user_id, posted_user_password = request.POST['user_id'], request.POST['user_password']

    # パスワード、uuid
    user_info_row = NewMyfit.user_mst().find_one({'uid': posted_user_id}, {'uuid': 1, 'pwd': 1, 'salt': 1, '_id': 0})

    # 該当ユーザが存在
    if user_info_row:

      uuid, pwd, salt = user_info_row['uuid'], user_info_row['pwd'], user_info_row['salt']

      if self.check_pwd(posted_user_password, salt, pwd):

        # 時間割情報
        user_data = NewMyfit.stu_mst().find_one({'uuid': uuid}, {'class': 1, 'grade': 1})

        return HttpResponse(json.dumps({
          'userUid': uuid,
          'userClass': user_data['class'],
          'userGrade': user_data['grade']
        }))

    return HttpResponse(json.dumps({'auth_res': False}))

    # パスワードのハッシュ値比較
  @staticmethod
  def check_pwd(row_pwd, salt, saved_pwd):
    hashed_pwd = pbkdf2(row_pwd, salt, iterations=120000, digest=hashlib.sha256)
    hashed_pwd = base64.b64encode(hashed_pwd).decode('ascii').strip()
    return hashed_pwd == saved_pwd


# ユーザの新規登録
class UserSignup(View):

  def post(self, request):

    user_id, user_password = request.POST['user_id'], request.POST['user_password']

    # uuidの作成
    uuid = hashlib.sha256(user_id.encode() + user_password.encode()).hexdigest()

    # ハッシュ後のパスワードとソルト値
    resulted_message = hash.make_password(user_password).split('$')[2:4]

    # 新ユーザの登録
    NewMyfit.user_mst().insert({
      'uuid': uuid,
      'uid': user_id,
      'pwd': resulted_message[1],
      'right': 0,
      'auto_auth': '',
      'salt': resulted_message[0]
    })

    # session初期化用
    session_info = {
      'userUid': uuid
    }
    return HttpResponse(json.dumps(session_info))


# 自動ユーザに認証
class AutoLogin(View):

  @staticmethod
  def post(request):
    user_uuid = request.POST['user_uuid']

    user = NewMyfit.user_mst().find_one({'uuid': user_uuid}, {'uuid': 1, '_id': 0})

    if user:
      user_data = NewMyfit.stu_mst().find_one({'uuid': user['uuid']}, {'class': 1, 'grade': 1})
      return HttpResponse(json.dumps({
        'userUid': user['uuid'],
        'userClass': user_data['class'],
        'userGrade': user_data['grade']
      }))

    return HttpResponse(json.dumps({'auth_res': False}))


# 時間割の表示
class TimeTable(View):

  @staticmethod
  def get(request):
    user_uuid = request.GET.get('user_uuid')
    time_table = NewMyfit.stu_mst().find_one({'uuid': user_uuid}, {'pro_time_table': 1, 'pro_credit_num': 1, '_id': 0})
    # pprint.pprint(time_table['pro_time_table'])
    return HttpResponse(json.dumps({'timeTable': time_table['pro_time_table'], 'creditNum': time_table['pro_credit_num']}))
