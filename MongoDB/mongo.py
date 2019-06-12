
from pymongo import MongoClient
import urllib.parse

username = urllib.parse.quote_plus('newmyfit')
password = urllib.parse.quote_plus('jveuirgvTS')

databasename = "newMyfit"
collection = "user_mst"

# databasename = "myNewDatabase"
# collection = "myCollection"
client = MongoClient('localhost',
                     username=username,
                     password=password,
                     authSource=databasename,
                     authMechanism='SCRAM-SHA-256')

db = client[databasename]
# db = client['myNewDatabase']

class NewMyfit():

  # user_mst collection
  @staticmethod
  def user_mst():
    return db['user_mst']


  # stu_mst collection
  @staticmethod
  def stu_mst():
    return db['stu_mst']
