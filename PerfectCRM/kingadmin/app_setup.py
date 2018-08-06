from django import conf

def kingadmin_auto_discover():
    for app_name in conf.settings.INSTALLED_APPS:
        # 遍历setting配置中的各app，找到app下的'kingadmin_tags.py'，如有，则导入，如没有则报错：ImportError
        # mod = importlib.import_module(app_name, 'kingadmin')
        try:
            #try 找到各APP中的Kingadmin.py文件，没找到的pass处理 __import__ 等价于 importlib.import_module(app_name, 'kingadmin')
            mod =__import__("%s.kingadmin"%app_name)
            # print(mod.kingadmin) # <module 'crm.kingadmin' from 'C:\\Users\\Administrator\\Desktop\\PerfectCRM\\crm\\kingadmin_tags.py'>

        except ImportError:
            pass
