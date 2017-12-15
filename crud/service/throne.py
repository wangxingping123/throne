from django.shortcuts import HttpResponse,render
class CrudConfig(object):

    list_display=[]   #自定义显示列
    def __init__(self,model_class,site):
        self.model_class=model_class
        self.site=site

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
        print(patterns)
        return patterns

    def changelist_view(self,request,*args,**kwargs):

        #处理表头的数据
        def headview():
            if not self.list_display:
                yield self.model_class._meta.model_name
            for field_name in self.list_display:
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
                for field_name in self.list_display:
                    if isinstance(field_name,str):
                        val=getattr(obj,field_name) #val是每个对象字段对应的值
                    else:
                        val=field_name(self,obj)
                    temp.append(val)
                yield temp
            if not self.list_display:
                for obj in data_list:
                    yield [obj,]
        return render(request,"crud/changelist.html",{"data_list":data_view(),"head_list":headview()})

    def add_view(self,request,*args,**kwargs):
        return HttpResponse("增加")
    def delete_view(self,request,*args,**kwargs):
        return HttpResponse("删除")
    def change_view(self,request,*args,**kwargs):
        return HttpResponse("修改")


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