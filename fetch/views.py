
"""
DBからユーザのお知らせ情報や
授業情報を取得し、クライアントへ送信するView
"""

from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
# Create your views here.

import json

from DB.mongo import NewMyfit

import sys
sys.path.append('../DB')


class StuNoticeInfo(View):

    def post(self, request):
        user_uid = request.POST['userUid']
        notice_info = self.extract_notice_info(user_uid)
        return HttpResponse(json.dumps({'noticeInfo': notice_info}))

    @staticmethod
    def extract_notice_info(user_uid):
        user_data_detail = NewMyfit.stu_mst().find_one({'user_uid': user_uid}, {'notice_info': 1, '_id': 0})
        return user_data_detail['notice_info']


class StuClassInfo(View):

    def post(self, request):

        user_uid = request.POST['userUid']
        class_info = self.extract_class_info(user_uid)
        return HttpResponse(json.dumps({'classInfo': class_info}))

    @staticmethod
    def extract_class_info(user_uid):
        print('check user_uid', user_uid)
        user_data_detail = NewMyfit.stu_mst().find_one({'user_uid': user_uid}, {'class_info': 1, '_id': 0})
        return user_data_detail['class_info']
