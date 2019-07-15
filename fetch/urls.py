
from django.urls import path
from .views import (
  StuNoticeInfo, StuClassInfo
)

urlpatterns = [
  path('stu_notice_info', StuNoticeInfo.as_view(), name='fetch-stu-notice-info'),
  path('stu_class_info', StuClassInfo.as_view(), name='fetch-stu-class-info')
]
