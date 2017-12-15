from django.shortcuts import HttpResponse,render,redirect
from django.utils.safestring import mark_safe
from django.urls import reverse
from django.forms import ModelForm
class CrudConfig(object):

    list_display=[]   #自定义显示列
    show_add_btn=True  #是否显示添加按钮
    model_form_class=None #自定义modelform类

    def __init__(self,model_class,site):
        self.model_class=model_class
        self.site=site


    def checkbox(self,obj=None,is_header=False):
        if is_header:
            return "#"
        return  mark_safe('<input type="checkbox" name="pk" value="%s">'%obj.id)

    def editor(self,obj=None,is_header=False):
        if is_header:
            return "操作"
        return  mark_safe('<a href="%s">修改</a>'%self.get_change_url(obj.id))

    def delete(self, obj=None, is_header=False):
        if is_header:
            return "操作"
        return mark_safe('<a href="%s">删除</a>'%self.get_delete_url(obj.id))
    #  URL相关
    def get_urls(self):
        '''自动生成url'''
        from django.conf.urls import url
        app_model_name=self.model_class._meta.app_label,self.model_class._meta.model_name
        patterns=[
            url(r'^$', self.changelist_view,name='%s_%s_changelist'%app_model_name),
            url(r'^add/$', self.add_view, name='%s_%s_add' % app_model_name),
            url(r'^delete/(\d+)/$', self.delete_view, name='%s_%s_delete' % app_model_name),
            url(r'^change/(\d+)/$', self.change_view, name='%s_%s_change' % app_model_name),
        ]
        patterns.extend(self.extra_url())  #扩展的url
        return patterns

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
    def extra_url(self):
        '''url的扩展'''
        return []
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
    def changelist_view(self,request,*args,**kwargs):

        #处理表头的数据
        def headview():
            if not self.list_display:
                yield self.model_class._meta.model_name
            for field_name in self.get_list_display():
                if isinstance(field_name,str):
                    #根据类和对象名获取字段对象的verbose_name
                    yield self.model_class._meta.get_field(field_name).verbose_name
                else:
                    yield field_name(self,is_header=True)
        #处理表中的数据
        def data_view():
            data_list=self.model_class.objects.all()  #当前表中所对应记录的query_set对象
            for obj in data_list:
                temp=[]
                for field_name in self.get_list_display():
                    if isinstance(field_name,str):
                        val=getattr(obj,field_name) #val是每个对象字段对应的值
                    else:
                        val=field_name(self,obj)
                    temp.append(val)
                yield temp
            if not self.list_display:
                for obj in data_list:
                    yield [obj,]
        return render(request,"crud/changelist.html",{"data_list":data_view(),"head_list":headview(),"add_url":self.get_add_url(),"show_add_btn":self.get_show_add_btn()})

    def add_view(self,request):
        formclass=self.get_model_form_class() #获取model_class
        if request.method=="GET":
            form = formclass()
        else:
            form=formclass(request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.get_changelist_url())
        return render(request, "crud/add.html", {"form": form})
    def delete_view(self,request,nid):
        self.model_class.objects.filter(pk=nid).delete()
        return redirect(self.get_changelist_url())
    def change_view(self,request,nid):
        formclass=self.get_model_form_class()
        obj=self.model_class.objects.filter(pk=nid).first()
        if not obj:
            return redirect(self.get_changelist_url())
        if request.method=="GET":
            form=formclass(instance=obj)
        else:
            form=formclass(instance=obj,data=request.POST)
            if form.is_valid():
                form.save()
                return redirect(self.get_changelist_url())
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