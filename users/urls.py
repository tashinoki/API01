
from django.urls import path
from . import views

from .views import (
  LoginAuth, UserSignup, AutoLogin, TimeTable
)

urlpatterns = [
  path('login', LoginAuth.as_view(), name='user-login'),
  path('new', UserSignup.as_view(), name='user-signup'),
  path('auto', AutoLogin.as_view(), name='user-auto-login'),
  path('pro_timetable', TimeTable.as_view(), name='user-timetable')
]
