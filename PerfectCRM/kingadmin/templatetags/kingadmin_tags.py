from django.template import Library
from django.utils.safestring import mark_safe
import datetime,time

register = Library()


@register.simple_tag
def get_model_name(admin_class):
    """获取表名"""
    return admin_class.model._meta.model_name

@register.simple_tag
def get_model_verbose_name(admin_class):
    """
    中文表名
    verbose_name:单数
    verbose_name_plural：复数
    """

    # return admin_class.model._meta.verbose_name
    return admin_class.model._meta.verbose_name_plural





@register.simple_tag
def get_obj_field_val(form_obj,admin_class,field):
    """
    返回model obj具体字段的值
    form_obj = model_form(instance = obj):正在被操作的字段（关键字：instance）
    getattr(form_obj.instance,field)：getattr(（正被操作的）对象,field（名称）)，映射某对象中某属性的值
    """
    column_obj = admin_class.model._meta.get_field(field)
    # 如果column_obj中字段对象有choices值，
    if column_obj.choices:
        # get_status_display：获取该字段对象中choices内的内容值 → (0,'你好'),非数字列表
        column_data = getattr(form_obj.instance, "get_%s_display" % field)()

    else:
        column_data = getattr(form_obj.instance,field)
    return column_data
    # return getattr(form_obj.instance,field)






@register.simple_tag
def build_table_row(obj,admin_class):
    """
    生成自定义标签，用于前端显示各表中数据
    """
    ele = ""
    if admin_class.list_display:#如果有list_display，则按list_display要求显示数据，如没有list_display，则返回对象str方法
        for index, column_name in enumerate(admin_class.list_display):
            """
           admin_class = RoleAdmin
           admin_class.model = model_class(如：model.Role)
           models.Role._meta.fields:获取model一个表中所有字段相对应的对象
           models.Role._meta.get_field('status'):取表中单个字段的对象
           """
            column_obj = admin_class.model._meta.get_field(column_name)
            # 如果column_obj中字段对象有choices值，
            if column_obj.choices:
                # get_status_display：获取该字段对象中choices内的内容值 → (0,'你好'),非数字列表
                column_data = getattr(obj, "get_%s_display" % column_name)()

            else:
                #将obj对象中的column_name属性值返回
                column_data = getattr(obj , column_name)

            td_ele = "<td>%s</td>" % column_data
            if index == 0:
                td_ele = "<td><a href='%s/change/'>%s</a></td>"% (obj.id,column_data)
            # if index == 1:
            #     td_ele = "<td><a href='%s/change/'>%s</a></td>"% (obj.id,obj)

            ele += td_ele

    else:
        td_ele = "<td><a href='%s/change/'>%s</a></td>" % (obj.id,obj)
        ele += td_ele

    return mark_safe(ele)


@register.simple_tag
def build_filter_ele(filter_column,admin_class):
    """
    用于前端显示过滤选择
    :param filter_column: 模板表中list_filter对象中的每一条数据，list_filter = ['source','consultant','status','date']
    :param admin_class.model = models.CustomerInfo
    odels.CustomerInfo._meta.get_field('status'):取一个字段的对象
    """
    column_obj = admin_class.model._meta.get_field(filter_column)

    try:
        filter_ele = "<select name='%s' class='btn' style='border: 1px solid #e4dada'>" %filter_column
        # column_obj.get_choices()是个方法，获取该字段对象中的choices所有内容（0，‘你好’）
        # 如该字段对象是外键关联，没有choices属性，则获取关联的外表的所有数据
        for choice in column_obj.get_choices():
            selected = ''
            if filter_column in admin_class.filter_condtions: #当前字段被过滤了
                #admin_class.filter_condtions.get(filter_column):结果是字符串'0','1'等，即str(choice[0])  ，choices：（0，‘你好’），（1，‘嗯嗯’）...
                if str(choice[0]) == admin_class.filter_condtions.get(filter_column): #当前值被选中了
                    selected = 'selected'
            option = "<option value='%s' %s>%s</option>"%(choice[0],selected,choice[1])
            filter_ele += option

    except AttributeError as e:
        # filter_ele = "<select name='%s__gte' class='btn btn-success'>" % filter_column
        # get_internal_type()：date时间类型判断:'DateField','DateTimeField'
        filter_ele = "<select name='%s__gte' class='btn' style='border: 1px solid #e4dada'>" % filter_column
        if column_obj.get_internal_type() in ('DateField','DateTimeField'):
            time_obj = datetime.datetime.now()
            time_list = [
                ['','----------'],
                [time_obj,'Today'],
                [time_obj - datetime.timedelta(7),'七天内'],
                [time_obj.replace(day=1),'本月'],
                [time_obj - datetime.timedelta(90),'三个月内'],
                [time_obj.replace(month=1,day=1),'YearToDay(YTD)'],
                ['','ALL'],
            ]

            for i in time_list:
                selected = ''
                # filter_condtions.get("%s__gte" % filter_column)获得日期格式是：Y-m-d ， name_gte：大于或等于
                #time_to_str = Y-m-d (2018-5-18)
                #http://127.0.0.1:8000/kingadmin/crm/customerinfo/?source=&consultant=&status=&date__gte=2018-5-12
                time_to_str = '' if not i[0] else "%s-%s-%s" % (i[0].year, i[0].month, i[0].day)
                if "%s__gte" % filter_column in admin_class.filter_condtions:  # 当前字段被过滤了
                    # print('-------------gte')
                    if time_to_str == admin_class.filter_condtions.get("%s__gte" % filter_column):  # 当前值被选中了
                        selected = 'selected '
                option = "<option value='%s' %s>%s</option>" %(time_to_str, selected, i[1])
                filter_ele += option

    filter_ele += "</select>"
    return mark_safe(filter_ele)




@register.simple_tag
def render_filtered_args(admin_class,render_html=True):
    '''在点击排序那行，拼接筛选的字段'''
    if admin_class.filter_condtions:
        ele = ''
        for k,v in admin_class.filter_condtions.items():
            ele += '&%s=%s' %(k,v)
        if render_html:
            return mark_safe(ele)
        else:
            return ele
    else:
        return ''

@register.simple_tag
def get_sorted_column(column,sorted_column,forloop):
    """
    排序功能,前端显示排序效果
    :param column: 当前各列，for循环实现
    :param sorted_column: 当前排序列
    :param forloop:
    :return:
    """
    if column in sorted_column:#这一列被排序了,
        #你要判断上一次排序是什么顺序,本次取反
        last_sort_index = sorted_column[column]
        #如果是‘-’号开始，eg:-1 、-2
        if last_sort_index.startswith('-'):
            this_time_sort_index = last_sort_index.strip('-')
        else:
            this_time_sort_index = '-%s' % last_sort_index
        return this_time_sort_index
    return forloop


@register.simple_tag
def get_current_sorted_column_index(sorted_column):
    """排序与过滤结合使用"""

    return list(sorted_column.values())[0] if sorted_column else ''


@register.simple_tag
def render_sorted_arrow(column,sorted_column):
    """排序列显示升序或降序符号"""
    if column in sorted_column:  # 这一列被排序了,
        last_sort_index = sorted_column[column]
        if last_sort_index.startswith('-'):
            arrow_direction = 'bottom'
        else:
            arrow_direction = 'top'
        ele = '''<span class="glyphicon glyphicon-triangle-%s" aria-hidden="true"></span>''' % arrow_direction
        return mark_safe(ele)
    return ''

@register.simple_tag
def render_filtered_args(admin_class,render_html=True):
    '''在前端点击排序那行，拼接筛选的字段'''
    if admin_class.filter_condtions:
        ele = ''
        for k,v in admin_class.filter_condtions.items():
            ele += '&%s=%s' %(k,v)
        if render_html:#如果是前端渲染页面，则返回这步
            return mark_safe(ele)
        else:#不是渲染页面，返回这步
            return ele
    else:
        return ''

@register.simple_tag
def render_paginator(querysets,admin_class,sorted_column):
    """
    分页功能
    从views中拿到querysets
    paginator = Paginator(querysets, 2) ：一页显示2行
    querysets = paginator.page(page)：当前页码
    """
    # 拿出搜索条件中的信息，添加进分页，实现点击分页时，搜索、筛选、排序及分页结合使用
    search_ele = '&_q=%s'%admin_class.search_key

    # 拿到筛选条件中的标签信息，添加进分页中，实现筛选时能结合分页一起使用
    filter_ele = render_filtered_args(admin_class)

    # 拿到排序列的信息，添加进分页，实现筛选、排序、分页一起结合使用
    sorted_ele = ''
    if sorted_column:  # 当前排序列信息
        sorted_ele = '&_o=%s' % list(sorted_column.values())[0]
    ele = '''
        <nav aria-label="Page navigation">
            <ul class="pagination">
                <li>
                    <a href="?_page=1%s%s%s" aria-label="shouye">
                        <span aria-hidden="true">首页</span>
                    </a>
                </li>
    '''%(search_ele,filter_ele,sorted_ele)
    if querysets.has_previous():
        p_ele = '''
        <li><a href="?_page=%s%s%s%s" aria-label="Previous">&laquo;上一页</a></li>
        ''' % (querysets.previous_page_number(),search_ele,filter_ele,sorted_ele)
        ele += p_ele
    # querysets.paginator=paginator，page_range:页数范围
    for i in querysets.paginator.page_range:
        # querysets.number:当前页码

        if abs(querysets.number - i) < 3:# 只显示相邻页码，最多2页
            active = ''
            # 当前页
            if querysets.number ==i :
                active = 'active'
            # # 拿到筛选条件中的标签信息，添加进分页中，实现筛选时能结合分页一起使用
            # filter_ele = render_filtered_args(admin_class)
            #
            # # 拿到排序列的信息，添加进分页，实现筛选、排序、分页一起结合使用
            # sorted_ele = ''
            # if sorted_column:# 当前排序列信息
            #     sorted_ele = '&_o=%s' % list(sorted_column.values())[0]
            p_ele = '''
            <li class="%s"><a href="?_page=%s%s%s%s">%s</a></li>
            '''% (active,i,search_ele,filter_ele,sorted_ele,i)
            ele += p_ele
        #是否有下一页
    if querysets.has_next():
        p_ele = '''
            <li><a href="?_page=%s%s%s%s" aria-label="Next">下一页&raquo;</a></li>
             ''' % (querysets.next_page_number(),search_ele,filter_ele,sorted_ele)
        ele += p_ele

        #querysets.paginator.num_pages：总页数
    p_ele = '''
        <li>
            <a href="?_page=%s%s%s%s" aria-label="weiye">
                <span aria-hidden="true">尾页</span>
            </a>
        </li>
    '''% (querysets.paginator.num_pages,search_ele,filter_ele,sorted_ele)
    ele += p_ele

    ele += "</ul></nav>"
    return mark_safe(ele)







#filter_horizontal相关操作
@register.simple_tag
def get_available_m2m_data(field_name,form_obj,admin_class):
    """
    返回的是m2m字段关联表的所有数据
    filter_horizontal = ['consult_courses', ]
    field_obj:拿到consult_courses字段的对象（一个对象）
    field_obj.related_model：拿到consult_courses关联的表对象
    field_obj.related_model.objects.all()：获取关联表的所有数据（queryset对象，打印课程名称）
    set()：集合
    """

    field_obj = admin_class.model._meta.get_field(field_name)
    # print("field_obj----:",field_obj)
    obj_list = set(field_obj.related_model.objects.all())
    # obj_list = field_obj.related_model.objects.all()

    if form_obj.instance.id:#当前对象存在，不是添加操作
        selected_data = set(getattr(form_obj.instance ,field_name).all())

        return obj_list - selected_data
    else:
        return obj_list



@register.simple_tag
def get_selected_m2m_data(field_name,form_obj,admin_class):
    """
    返回已选的m2m数据
    getattr(form_obj.instance ,field_name)：field_name=consult_courses，  getattr（'对象','名称'），名称如果是外键，则获得该对象中外键对应
                                            的表对象
    getattr(form_obj.instance ,field_name).all()：获取该外键关联表内（属于该对象的）所有数据
    """

    if form_obj.instance.id:
        selected_data = getattr(form_obj.instance ,field_name).all()

        return selected_data

    else:
        return []





# 删除操作
@register.simple_tag
def display_all_related_objs(obj):
    """
    显示要被删除对象的所有关联对象
    :param obj:
    :return:
    """
    ele = "<ul><b style='color:red'>%s</b>" % obj
    # ele += "<li><a href='/kingadmin/%s/%s/%s/change/'>%s</a></li>" %(obj._meta.app_label,
    #                                                                  obj._meta.model_name,
    #                                                                  obj.id,obj)
    """
    obj = admin_class.model.objects.get(id=obj_id)
    obj._meta.related_objects:拿到obj被关联的所有一对一、多对一、多对多的表[ManyToMany、ManyToOne]，多对一是指己方表被别的表关联
    reversed_fk_obj.name：拿到主动关联表的表名(含有fk外键关联的)
    getattr(obj,related_lookup_key).all() ：getattr(obj,Role_set).all()，反向查关联表的所有关联的数据[queryset集合]
    reversed_fk_obj.get_internal_type():判断表类型，ForeignKey、ManyToManyField
    getattr(obj,related_lookup_key).all()= obj.Role_set.all()
    """

    for reversed_fk_obj in obj._meta.related_objects:

        if reversed_fk_obj.get_internal_type() == "OneToOneField":  # 一对一或者一对多不需要操作，多对一、多对多需要下述操作
            continue
        else:
            related_table_name =  reversed_fk_obj.name
            related_lookup_key = "%s_set" % related_table_name
            related_objs = getattr(obj,related_lookup_key).all() #反向查所有关联的数据
            ele += "<li>%s<ul> "% related_table_name

        # if reversed_fk_obj.get_internal_type() == "OneToOneField":  # 一对一或者一对多不需要操作，多对一、多对多需要下述操作


            if reversed_fk_obj.get_internal_type() == "ManyToManyField":  # 不需要深入查找
                for i in related_objs:
                    ele += "<li><a href='/kingadmin/%s/%s/%s/change/'>%s</a> 记录里与[%s]相关的的数据将被删除</li>" \
                        % (i._meta.app_label,i._meta.model_name,i.id,i,obj)
            else:
                for i in related_objs:
                    #ele += "<li>%s--</li>" %i
                    ele += "<li><a href='/kingadmin/%s/%s/%s/change/'>%s</a></li>" %(i._meta.app_label,
                                                                                 i._meta.model_name,
                                                                                 i.id,i)
                    ele += display_all_related_objs(i)

            ele += "</ul></li>"

        ele += "</ul>"

    return ele