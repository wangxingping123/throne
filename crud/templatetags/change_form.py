from django.template import Library
from django.urls import reverse
from crud.service.throne import site
from django.forms import ModelChoiceField
register=Library()

@register.inclusion_tag('crud/form.html')
def form(model_form_obj):
    new_form=[]

    for bfield in model_form_obj:
        temp = {'is_popup': False, 'item': bfield}
        if isinstance(bfield.field, ModelChoiceField):   #判断当前字段是否是一对多和多对多字段
            related_class_name = bfield.field.queryset.model #取出当前字段所在的类名
            if related_class_name in site._registry:    #判断当前类是否被注册
                app_model_name = related_class_name._meta.app_label, related_class_name._meta.model_name
                baseurl = reverse("crud:%s_%s_add" % app_model_name)
                popurl = '%s?popback_id=%s' % (baseurl, bfield.auto_id)
                temp["is_popup"] = True
                temp["popurl"] = popurl

        new_form.append(temp)
    return {"form":new_form}
