from kingadmin import permission_hook

perm_dic= {

    'crm_app_index': ['app_index', 'GET', [], {}, ],  # 可以查看profect home 下的所有数据库表
    'crm_crm_index': ['crm_index', 'GET', [], {}, ],  # 可以查看CRM APP里所有数据库表
    # 'crm_own_table_list': ['table_obj_list', 'GET', [], {},permission_hook.view_my_own_customers],  # 可以查看指定表里所有的数据
    'crm_table_list': ['table_obj_list', 'GET', [], {}],  # 可以查看每张表里所有的数据
    'crm_table_delete': ['obj_delete', 'GET', [], {}],  # 可以对表里的每条数据进行删除
    'crm_table_list_view': ['table_obj_change', 'GET', [], {}],  # 可以访问表里每条数据的修改页
    'crm_table_list_change': ['table_obj_change', 'POST', [], {}],  # 可以对表里的每条数据进行修改
    'crm_table_obj_add_view': ['table_obj_add', 'GET', [], {}],  # 可以访问数据增加页
    'crm_table_obj_add': ['table_obj_add', 'POST', [], {}],  # 可以创建表里的数据


}



