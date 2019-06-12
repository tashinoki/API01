from django.shortcuts import render
from django.http import HttpResponse
from django.views.generic import View
from .models import Class

import pprint
import json

# 親ディレクトリを追加する
import sys
sys.path.append('../MongoDB')

# mongo DB 関連module
from MongoDB.mongo import NewMyfit

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

    pprint.pprint(user_info)

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
