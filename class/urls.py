
from django.urls import path
from .views import (
  TImeTableDetail, TImeTableEdit, TimeTableUpdate
)

urlpatterns = [
  path('timetable_detail', TImeTableDetail.as_view(), name='timetable-detail'),
  path('timetable_edit', TImeTableEdit.as_view(), name='timetable-edit'),
  path('timetable_update', TimeTableUpdate.as_view(), name='timetable-update'),
]
