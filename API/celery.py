
"""
Celeryを使った非同期処理
https://dot-blog.jp/news/django-async-celery-redis-mac/
"""

import os
from celery import Cerely

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'API.settings')
app = Cerely('')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
