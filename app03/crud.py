from crud.service import throne
from app03 import models

class UserInfoConfig(throne.CrudConfig):

    def display_gender(self,condition=None,obj=None,is_header=None):
        if is_header:
            return "性别"
        return obj.get_gender_display()
    def display_roles(self,condition=None,obj=None,is_header=None):
        if is_header:
            return "角色"
        role_list=[]
        for role in obj.roles.all():
            role_list.append(role.title)
        return ','.join(role_list)

    comb_filter = [throne.FilterOption("gender",is_choices=True),
                   throne.FilterOption("depart"),
                   throne.FilterOption("roles",is_multi=True)]

    list_display = ["id","name","email",display_gender,"depart",display_roles]


throne.site.register(models.UserInfo,UserInfoConfig)


class DepartmentConfig(throne.CrudConfig):
    list_display = ["id","caption"]


throne.site.register(models.Department,DepartmentConfig)

class RoleConfig(throne.CrudConfig):
    list_display = ["id","title"]

throne.site.register(models.Role,RoleConfig)