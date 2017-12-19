from django.db import models

class Student(models.Model):
    name=models.CharField(verbose_name="姓名",max_length=32)
    gender_choice=((1,"男"),(2,"女"))
    gender=models.IntegerField(verbose_name="性别",choices=gender_choice)
    age=models.IntegerField(verbose_name="年龄")

