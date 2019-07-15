from django.db import models


# Create your models here.
class Class(models.Model):

    # 授業コード
    class_code = models.IntegerField(primary_key=True)
    # 授業名
    class_name = models.CharField(max_length=50)
    # 担当教授
    teacher = models.CharField(max_length=50)
    # 学科名
    depart = models.CharField(max_length=50)
    # 開講時期
    section = models.CharField(max_length=50)
    # 曜日
    week_day = models.CharField(max_length=50)
    # 時限
    time = models.IntegerField()
    # 教室
    room = models.CharField(max_length=50)
    # 学年
    grade = models.IntegerField()
    # 必修科目
    required = models.BooleanField()
    # 取得単位
    credit = models.IntegerField()
    # 区分
    division = models.CharField(max_length=50)
    # 組
    classes = models.IntegerField()
    # シラバス
    syllabus = models.TextField(max_length=1000, null=True)
    # 内容
    content = models.TextField(max_length=1000, null=True)
