
from django.urls import path

from .views import (
  LoginAuth, AutoLogin, TimeTable, XsrfTokenIssue
)

urlpatterns = [
  path('', XsrfTokenIssue.as_view(), name='xsrf-token-issue'),
  path('login', LoginAuth.as_view(), name='user-login'),
  path('auto', AutoLogin.as_view(), name='user-auto-login'),
  path('pro_timetable', TimeTable.as_view(), name='user-timetable')
]
