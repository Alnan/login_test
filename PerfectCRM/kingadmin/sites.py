from kingadmin.admin_base import BaseKingAdmin


class AdminSite(object):
    def __init__(self):
        self.enabled_admins = {}


    def register(self,model_class,admin_class=None):
        """
        注册表:
        site.register(models.CustomerInfo,CustomerAdmin)
        :param model_class: models.CustomerInfo
        :param admin_class: CustomerAdmin
        model_class._meta.app_label = models.CustomerInfo._meta.app_label ：获取对应APP名称
        model_class._meta.model_name = models.CustomerInfo._meta.model_name ：获取对应表名称
        """

        app_name = model_class._meta.app_label
        model_name = model_class._meta.model_name

        if not admin_class: # 为了避免多个model共享同一个BaseKingAdmin内存对象
            # 实例化BaseKingAdmin对象，每一次循环此语句都开辟一块新内存
            admin_class = BaseKingAdmin()

        else:
            # 实例化 CustomerAdmin 对象
            admin_class = admin_class()

        admin_class.model = model_class # 把model_class赋值给了admin_class

        if app_name not in self.enabled_admins:
            self.enabled_admins[app_name] = {}

        # enabled_admins中存的是字典（字典中套字典）：crm:{ {'CustomerInfo':'CustomerAdmin'} , {'Role':'RoleAdmin'}}
        # enabled_admins[crm][CustomerInfo] = CustomerAdmin
        self.enabled_admins[app_name][model_name] = admin_class


site = AdminSite()