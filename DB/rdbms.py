
"""
MySQL接続モジュール
"""

from urllib.parse import urlparse
import mysql.connector

url = urlparse('mysql://kinoshita:fMxJUM6G@localhost:3306/newmyfit')

conn = mysql.connector.connect(
    host=url.hostname or 'localhost',
    port=url.port or 3306,
    user=url.username or 'root',
    password=url.password or 'root',
    database=url.path[1:],
)
