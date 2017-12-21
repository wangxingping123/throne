import copy
import json
from django.shortcuts import HttpResponse,render,redirect
from django.utils.safestring import mark_safe
from crud.service.pager import Pagination
from django.urls import reverse
from django.forms import ModelForm
from django.http import QueryDict
from django.db.models import Q

class FilterOption(object):
    '''
    用户在传组合搜索子段时调用，
    参数  field:组合搜索的字段名名
        is_choices:是否是选择类型
        is_multi:是否是多选类型
        condition:过滤条件
    '''
    def __init__(self,field_name,is_choices=False,is_multi=False,condition=None):
        self.field_name=field_name
        self.is_choices=is_choices
        self.is_multi=is_multi
        self.condition=condition

    def get_queryset(self,_field):
        #处理关联字段的函数
        if self.condition:
            return _field.rel.to.objects.filter(**self.condition)
        return _field.rel.to.objects.all()

    def get_choices(self,_field):
        #处理选择的字段
        return _field.choices

class FilterRow(object):
    '''这个类用来处理用户传出组合搜索字段下的数据'''
    def __init__(self,changelist_obj,datalist,field_obj,request):
        self.changelist_obj=changelist_obj
        self.datalist=datalist
        self.field_obj=field_obj
        self.request=request

    def __iter__(self):
        #取出对应的字段名
        field_name=self.field_obj.field_name
        verbose_name=self.changelist_obj.model_class._meta.get_field(field_name).verbose_name
        yield mark_safe('<span class="verbose_name">%s:</span>'%verbose_name)
        params=copy.deepcopy(self.request.GET)   #拷贝当前过滤条件
        params.mutable=True   #可更改状态
        current_id=self.request.GET.get(self.field_obj.field_name,'')
        current_id_list=self.request.GET.getlist(self.field_obj.field_name,'')
        if self.field_obj.field_name in params:
            origin_list=params.pop(self.field_obj.field_name)
            url='<a href="{0}?{1}">全部</a>'.format(self.request.path_info,params.urlencode())
            yield mark_safe(url)
            params.setlist(self.field_obj.field_name, origin_list)
        else:
            url='<a class="active" href="{0}?{1}">全部</a>'.format(self.request.path_info,params.urlencode())
            yield mark_safe(url)

        for val in self.datalist:
            if self.field_obj.is_choices:
                pk, text = str(val[0]), val[1]
            else:
                pk, text = str(val.pk), str(val)
            if self.field_obj.is_choices:
                params[self.field_obj.field_name]=pk   #设置过滤条件
                if pk in current_id:
                    url=mark_safe('<a class="active" href="{0}?{1}">{2}</a>'.format(self.request.path_info,params.urlencode(),text))
                else:
                    url=mark_safe('<a href="{0}?{1}">{2}</a>'.format(self.request.path_info,params.urlencode(),text))
                yield url
            else:
                if not self.field_obj.is_multi:
                    params[self.field_obj.field_name]=pk  #设置过滤条件
                    if pk in current_id:
                        url = '<a class="active" href="{0}?{1}">{2}</a>'.format(self.request.path_info, params.urlencode(), text)
                    else:
                        url='<a href="{0}?{1}">{2}</a>'.format(self.request.path_info,params.urlencode(),text)
                    yield mark_safe(url)
                else:
                    #多选
                    _params = copy.deepcopy(params)
                    id_list = _params.getlist(self.field_obj.field_name)

                    if pk in current_id_list:
                        id_list.remove(pk)
                        _params.setlist(self.field_obj.field_name, id_list)
                        url = "{0}?{1}".format(self.request.path_info, _params.urlencode())
                        yield mark_safe("<a class='active' href='{0}'>{1}</a>".format(url, text))
                    else:
                        id_list.append(pk)
                        # params中被重新赋值
                        _params.setlist(self.field_obj.field_name, id_list)
            
                        # 创建URL
                        url = "{0}?{1}".format(self.request.path_info, _params.urlencode())
                        yield mark_safe("<a href='{0}'>{1}</a>".format(url, text))


class ChangeList(object):
    def __init__(self,config,request,data_list):
        self.request=request
        self.config=config
        self.list_display=self.config.list_display
        self.model_class=self.config.model_class
        self.get_list_display=self.config.get_list_display()
        # 过滤条件
        params = QueryDict(mutable=True)
        params["_filter_list"] = request.GET.urlencode()
        self.condition = params.urlencode()
        #分页
        self.data_count=data_list.count()
        self.get_changelist_url=self.config.get_changelist_url()
        page = Pagination(request.GET.get("page", 1), self.data_count, self.get_changelist_url, request.GET)
        self.show_data_list = data_list[page.start:page.end]
        self.page_html = page.page_html()
        #搜索相关
        self.search_key=self.config.search_key
        self.condition_key=request.GET.get(self.search_key,"")
    def show_search(self):
        return self.config.get_show_search()
    def show_add_btn(self):
        return self.config.get_show_add_btn()
    def show_actions(self):
        return self.config.get_show_actions()
    def add_url(self):
        return self.config.get_add_url()
    def mudify_actions(self):
        result=[]
        for func in self.config.actions:
            temp={"name":func.__name__,"text":func.short_desc}
            result.append(temp)
        return result

    #组合搜索
    def gen_comb_filter(self):

        from django.db.models import ForeignKey,ManyToManyField
        for field_obj in self.config.comb_filter:
            _field=self.model_class._meta.get_field(field_obj.field_name)
            if isinstance(_field,ForeignKey):
                filter_row_obj=FilterRow(self,field_obj.get_queryset(_field),field_obj,self.request)
            elif isinstance(_field,ManyToManyField):
                filter_row_obj = FilterRow(self,field_obj.get_queryset(_field), field_obj, self.request)
            else:
                filter_row_obj = FilterRow(self,field_obj.get_choices(_field), field_obj, self.request)

            yield filter_row_obj


    def get_header(self):
        # 生成表头的数据
        if not self.list_display:
            yield self.model_class._meta.model_name
        for field_name in self.get_list_display:
            if isinstance(field_name, str):
                # 根据类和对象名获取字段对象的verbose_name
                verbose_name= self.model_class._meta.get_field(field_name).verbose_name
            else:
                verbose_name= field_name(self.config, is_header=True)
            yield verbose_name

    def get_data_list(self):
        for obj in self.show_data_list:
            temp = []
            for field_name in self.get_list_display:
                if isinstance(field_name, str):
                    val = getattr(obj, field_name)  # val是每个对象字段对应的值
                else:
                    val = field_name(self.config, self.condition, obj)
                temp.append(val)
            yield temp
        if not self.list_display:
            for obj in self.show_data_list:
                a = mark_safe('<a href="%s?%s">%s</a>' % (self.config.config.get_change_url(obj.pk),self.condition, obj))
                yield [a, ]




class CrudConfig(object):

    list_display=[]   #自定义显示列
    show_add_btn=True  #是否显示添加按钮
    model_form_class=None #自定义modelform类
    search_key='key'    #自定义搜索的key
    search_condition=[] #自定义搜索的条件
    show_search=False    #是否显示搜索框

    def __init__(self,model_class,site):
        self.model_class=model_class
        self.site=site
        self.request=None

    def checkbox(self,condition=None,obj=None,is_header=False):
        if is_header:
            return mark_safe('<input type="checkbox" id="select_all">全选')
        return  mark_safe('<input type="checkbox" name="pk" value="%s">'%obj.pk)

    def editor(self,condition=None,obj=None,is_header=False):
        if is_header:
            return "操作"

        return  mark_safe('<a href="%s?%s">修改</a>'%(self.get_change_url(obj.pk),condition))

    def delete(self,condition=None, obj=None, is_header=False):
        if is_header:
            return "操作"
        return mark_safe('<a href="%s?%s">删除</a>'%(self.get_delete_url(obj.pk),condition))

    #搜索相关
    def get_search_condition(self):
        if self.search_condition:
            return self.search_condition
    def get_show_search(self):
        return self.show_search
    def get_conditions(self):
        #获取搜索条件
        condition = self.request.GET.get(self.search_key,"")
        conditions = Q()
        conditions.connector = "or"
        if self.search_condition:
            for item in self.search_condition:
                conditions.children.append((item, condition))
        return conditions

    #组合搜索
    comb_filter=[]   #自定义组合搜索的字段
    def get_comb_filter(self):
        result=[]
        if self.comb_filter:
            result.extend(self.comb_filter)
        return result

    #批量操作相关
    show_actions=False       #是否显示批量操作框
    def get_show_actions(self):
        return self.show_actions
    actions = []  # 自定义批量操作(参数是对应的函数名)
    def get_actions(self):
        result=[]
        if self.actions:
            result.extend(self.actions)
        return result

    #  URL相关
    #装饰器函数
    def wrapper(self,func):
        def inner(request,*args,**kwargs):
            self.request=request
            return func(request,*args,**kwargs)
        return inner
    def get_urls(self):
        '''自动生成url'''
        from django.conf.urls import url
        app_model_name=self.model_class._meta.app_label,self.model_class._meta.model_name
        patterns=[
            url(r'^$', self.wrapper(self.changelist_view),name='%s_%s_changelist'%app_model_name),
            url(r'^add/$', self.wrapper(self.add_view), name='%s_%s_add' % app_model_name),
            url(r'^delete/(\d+)/$', self.wrapper(self.delete_view), name='%s_%s_delete' % app_model_name),
            url(r'^change/(\d+)/$', self.wrapper(self.change_view), name='%s_%s_change' % app_model_name),
        ]
        patterns.extend(self.extra_url())  #扩展的url
        return patterns

    def extra_url(self):
        '''url的扩展'''
        return []

    def get_change_url(self,nid):
        name='crud:%s_%s_change'%(self.model_class._meta.app_label,self.model_class._meta.model_name)
        change_url=reverse(name,args=(nid,))
        return change_url

    def get_changelist_url(self):
        name = 'crud:%s_%s_changelist' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        changelist_url = reverse(name)
        return changelist_url

    def get_add_url(self):
        name = 'crud:%s_%s_add' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        add_url = reverse(name)
        return add_url

    def get_delete_url(self, nid):
        name = 'crud:%s_%s_delete' % (self.model_class._meta.app_label, self.model_class._meta.model_name)
        delete_url = reverse(name, args=(nid,))
        return delete_url

    def get_list_display(self):
        data=[]
        if self.list_display:
            data.extend(self.list_display)
            data.append(CrudConfig.editor)
            data.append(CrudConfig.delete)
            data.insert(0,CrudConfig.checkbox)
        return data

    #功能的自定制
    def get_show_add_btn(self):
        '''获取是否显示添加按钮'''
        return self.show_add_btn
    def get_model_form_class(self):
        '''modelclass的定制'''
        if self.model_form_class:
            return self.model_form_class
        class DefaultModelForm(ModelForm):
            class Meta:
                model=self.model_class
                fields="__all__"
        return DefaultModelForm


    #处理对应url的函数
    def changelist_view(self,request):

        if request.method=="POST" and self.get_show_actions():
            action=request.POST.get("action") #获取用户选择的批量操作
            func=getattr(self,action)          #找到对应的函数
            ret=func(request)
            if ret:
                return ret

        conditions=self.get_conditions()

        #取出组合搜索的过滤条件
        filter_dic={}
        for item in request.GET.keys():
            for obj in self.get_comb_filter():
                if item==obj.field_name:
                    filter_dic['%s__in'%item]=request.GET.getlist(item)
        data_list = self.model_class.objects.filter(conditions).filter(**filter_dic).distinct() # 当前表中所对应记录的query_set对象
        obj=ChangeList(self,request,data_list)

        return render(request,"crud/changelist.html",{"obj":obj})

    def add_view(self,request):

        popback_id=request.GET.get("popback_id")
        formclass=self.get_model_form_class() #获取model_class
        if request.method=="GET":
            form = formclass()

        else:
            condition=request.GET.get("_filter_list")
            form=formclass(request.POST)
            if form.is_valid():
                new_obj=form.save()
                if popback_id:
                    result = {'id': new_obj.pk, 'text': str(new_obj), 'popbackid': popback_id}
                    return render(request,"crud/pop_response.html",{"result":json.dumps(result)})
                return redirect('%s?%s'%(self.get_changelist_url(),condition))
        return render(request, "crud/add.html", {"form": form})
    def delete_view(self,request,nid):
        condition = request.GET.get("_filter_list")
        self.model_class.objects.filter(pk=nid).delete()
        return redirect('%s?%s'%(self.get_changelist_url(),condition))
    def change_view(self,request,nid):
        formclass=self.get_model_form_class()
        obj=self.model_class.objects.filter(pk=nid).first()
        if not obj:
            return redirect(self.get_changelist_url())
        if request.method=="GET":
            form=formclass(instance=obj)
        else:
            condition = request.GET.get("_filter_list")
            form=formclass(instance=obj,data=request.POST)
            if form.is_valid():
                form.save()
                return redirect('%s?%s'%(self.get_changelist_url(),condition))
        return render(request,"crud/change.html",{"form":form})

    @property
    def urls(self):
        return self.get_urls()


class CrudSite(object):
    def __init__(self):
        self._registry={}

    def register(self,model_class,crud_cofig_obj=None):
        '''将注册的类存在_registry字典中'''
        if not crud_cofig_obj:
            crud_cofig_obj=CrudConfig
        self._registry[model_class]=crud_cofig_obj(model_class,self)

    def get_urls(self):
         '''自动生成url'''
         from django.conf.urls import url, include
         patterns=[]
         for model_class,site_config_obj in self._registry.items():
             app_name=model_class._meta.app_label
             model_name=model_class._meta.model_name
             patterns+=[url(r'%s/%s/'%(app_name,model_name),(site_config_obj.urls,None,None))]
         return patterns
    @property
    def urls(self):

        return (self.get_urls(),"crud","crud")


site=CrudSite()