from crud.service import throne
from app01 import models
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import HttpResponse


class ListConfig(throne.CrudConfig):

    list_display = ["id","name"]
    def extra_url(self):

        url_list=[
            url(r'^xxx/', self.xxx),
        ]
        return url_list
    def xxx(self,request):
        return HttpResponse("xxx")

class HostConfig(throne.CrudConfig):

    list_display = ["id","ip","port","user"]
throne.site.register(models.UserInfo,ListConfig)
throne.site.register(models.Host,HostConfig)