from django.db import models

class UserInfo(models.Model):

    name=models.CharField(verbose_name="用户名",max_length=32)
    pwd=models.CharField(verbose_name="密码",max_length=32)

    def __str__(self):
        return self.name

class Host(models.Model):
    ip=models.GenericIPAddressField(verbose_name="ip")
    port=models.IntegerField(verbose_name="端口")
    user=models.ForeignKey(to=UserInfo,verbose_name="用户")

    def __str__(self):
        return self.user.name