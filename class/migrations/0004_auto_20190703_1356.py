# Generated by Django 2.1.7 on 2019-07-03 04:56

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('class', '0003_auto_20190703_1351'),
    ]

    operations = [
        migrations.AlterField(
            model_name='class',
            name='content',
            field=models.TextField(max_length=1000, null=True),
        ),
        migrations.AlterField(
            model_name='class',
            name='syllabus',
            field=models.TextField(max_length=1000, null=True),
        ),
    ]
