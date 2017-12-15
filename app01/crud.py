from crud.service import throne
from app01 import models
from django.utils.safestring import mark_safe

class ListConfig(throne.CrudConfig):

    def checkbox(self,obj=None,is_header=False):
        if is_header:
            return "#"
        return  mark_safe('<input type="checkbox" name="pk" value="%s">'%obj.id)

    list_display = [checkbox,"id","name"]

throne.site.register(models.UserInfo,ListConfig)