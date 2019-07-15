
from django.urls import path
from .views import (
  TImeTableDetail, TImeTableEdit, TimeTableUpdate, ClassSyllabus, ClassAttend
)

urlpatterns = [
  path('timetable_detail', TImeTableDetail.as_view(), name='timetable-detail'),
  path('timetable_edit', TImeTableEdit.as_view(), name='timetable-edit'),
  path('timetable_update', TimeTableUpdate.as_view(), name='timetable-update'),
  path('syllabus', ClassSyllabus.as_view(), name='class-syllabus'),
  path('attend', ClassAttend.as_view(), name='class-content')
]
