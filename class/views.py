
'''
時間割や授業情報に関するクラス
'''

from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from .models import Class

import pprint
import re
import json

# 親ディレクトリを追加する
import sys
sys.path.append('../DB')
sys.path.append('../module')

# mongo DB 関連module
from DB.mongo import NewMyfit
from module import scrape


# Create your views here.
class TImeTableDetail(View):

    @staticmethod
    def get(request):
        subject_code = request.GET.get('subjectCode')
        subject = Class.objects.filter(class_code=subject_code)[0]
        return HttpResponse(json.dumps({'teacher': subject.teacher, 'room': subject.room}))


# 時間割の編集要求
class TImeTableEdit(View):

    @staticmethod
    def get(request):

        subject_list = []

        params = request.GET
        user_info = {
          'user_uuid': params.get('userUuid'),
          'user_class': int(params.get('userClass')),
          'user_grade': int(params.get('userGrade')),
          'subject_day': params.get('subjectDay'),
          'subject_time': int(params.get('subjectTime'))
        }

        target_subject = Class.objects.filter(
          grade=user_info['user_grade'], time=user_info['subject_time'], week_day=user_info['subject_day']
        )

        for subject in target_subject:
            subject_list.append({
              'subjectName': subject.class_name, 'subjectCode': subject.class_code, 'teacher': subject.teacher,
              'room': subject.room, 'required': subject.required, 'credit': subject.credit, 'class': subject.classes,
              'division': subject.division
            })

        return HttpResponse(json.dumps(subject_list))


class TimeTableUpdate(View):

    @staticmethod
    def post(request):

        uuid, table_data = request.POST['userUid'], json.loads(request.POST['updatedTimetable'])
        NewMyfit.stu_mst().update({'uuid': uuid}, {'$set': {'pro_time_table': table_data}})

        return HttpResponse(json.dumps({'result': True}))


class ClassSyllabus(View):

    @staticmethod
    def get(request):
        class_code = request.GET['classCode']
        # print(class_code)
        subject = Class.objects.filter(class_code=class_code)[0]
        class_name =subject.class_name
        syllabus = subject.syllabus
        row_contents = subject.content.split('\r\n')
        contents = []

        '''
        正規表現を使たトリミングを行う
        無駄な空白や先頭の「1.」を取り除く
        片山先生の授業は「第〇週」の形になる
        '''

        for content in row_contents:
            content = content.replace('＊', '')
            content = re.sub('', '', content)

            contents.append(content)
            # print('line', line)

        # print(contents)
        return HttpResponse(json.dumps({'className': class_name, 'syllabus': syllabus, 'contents': contents}))


class ClassAttend(View):

    def post(self, request):

        user_uid = request.POST['userUid']
        fit_token = scrape.uid_to_token(user_uid)
        print('next', fit_token)
        html_element = scrape.create_html_element(fit_token=fit_token)
        # print(html_element)
        value = scrape.extract_sun_faces_view(html_element)
        print('value', value)
        scrape.extract_attend_info(fit_token, value)
        return HttpResponse()
