from django.shortcuts import render,redirect
from app02.utils.pager import Pagination
from app02 import models
from django.forms import ModelForm
from django.http import QueryDict
class StrudentForm(ModelForm):
    class Meta:
        model=models.Student
        fields="__all__"

def hosts(request):

    # page_num=int(request.GET.get("page",1))
    # show_count=10
    #
    # page_max,div=divmod(len(data_list),show_count)
    # if div:
    #     page_max+=1
    #
    # #每页显示的数据
    # page_list=[]  #页码
    # for i in range(1,page_max+1):
    #     if i == page_num:
    #         page_list.append('<a class="active" href="/hosts/?page=%s">%s</a>' % (i, i))
    #     else:
    #         page_list.append('<a href="/hosts/?page=%s">%s</a>'%(i,i))
    # pagelist=''.join(page_list)
    #
    # show_data_list=data_list[show_count*(page_num-1):page_num*show_count]


    data_list = models.Student.objects.all()
    pager_obj = Pagination(request.GET.get('page', 1), len(data_list), request.path_info, request.GET)
    student_list = data_list[pager_obj.start:pager_obj.end]
    html = pager_obj.page_html()


    params=QueryDict(mutable=True)
    params["_filter_list"]=request.GET.urlencode()
    condition=params.urlencode()
    return render(request,"hosts.html",{"student_list":student_list,"pagelist":html,"condition":condition})


def add(request):
    if request.method=="GET":
        form =StrudentForm()
    else:
        condition=request.GET.get("_filter_list")
        form=StrudentForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect("/hosts/?%s"%condition)
    return render(request, "add.html", {"form": form})

def editor(request,nid):
    student = models.Student.objects.filter(id=nid).first()
    if request.method=="GET":
        form=StrudentForm(instance=student)

    else:
        form=StrudentForm(data=request.POST,instance=student)
        if form.is_valid():
            form.save()
            return redirect('/hosts/?%s'%request.GET.get("_filter_list"))
    return render(request, "editor.html", {"form": form})