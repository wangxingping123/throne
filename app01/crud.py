from crud.service import throne
from app01 import models
from django.utils.safestring import mark_safe
from django.conf.urls import url
from django.shortcuts import HttpResponse,redirect


class ListConfig(throne.CrudConfig):
    search_condition=["id__contains","name__contains"]
    list_display = ["id","name"]
    def extra_url(self):

        url_list=[
            url(r'^xxx/', self.xxx),
        ]
        return url_list
    def xxx(self,request):
        return HttpResponse("xxx")
    def muti_del(self,request):
        pk_list = request.POST.getlist('pk')
        self.model_class.objects.filter(id__in=pk_list).delete()
        return redirect(self.get_changelist_url())
    muti_del.short_desc="批量删除"
    actions = [muti_del,]

class HostConfig(throne.CrudConfig):

    list_display = ["id","ip","port","user"]
throne.site.register(models.UserInfo,ListConfig)
throne.site.register(models.Host)