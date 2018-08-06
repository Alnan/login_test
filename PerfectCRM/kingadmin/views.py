from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,logout,login
from kingadmin import app_setup
from kingadmin.sites import site
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.db.models import Q
from kingadmin import form_handle
import json
from kingadmin import permissions


app_setup.kingadmin_auto_discover()
# print("site:     ",site.enabled_admins)

# Create your views here.

def acc_login(request):
    """登录页"""
    error_msg = ''
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")
        # remtime = request.POST.get("remtime")
        user = authenticate(username = username ,password = password)
        if user:
            login(request,user)
            # if remtime:
            #     request.session.set_expiry(10) #session失效时间

            #使用Django自带login_required装饰器，在登录页调整时url路径会有类似 next=/crm/ 数据，需获取到next值，
            #再通过redirect重定向到该页面，如无next值，则返回默认路径（如/crm/）
            # return redirect(request.GET.get("next","/crm/"))
            return redirect('/kingadmin/')
        else:

            error_msg = "Wrong username or password!"
    return render(request,"kingadmin/login.html",{"error_msg":error_msg})


def acc_logout(request):
    logout(request)
    return redirect("kingadmin/login/")

@permissions.check_permission
def app_index(request):
    """kingadmin下的首页"""
    return render(request,"kingadmin/app_index.html",{"site":site})



def get_filter_result(request,querysets):
    """
    用于 table_obj_list 过滤数据处理
    """
    filter_condtions = {}
    for key,val in request.GET.items():
        if key in ('_page', '_o', '_q'): continue
        if val:
            filter_condtions[key] = val

    return querysets.filter(**filter_condtions), filter_condtions

def get_orderby_result(request,querysets,admin_class):
    """排序功能"""

    current_ordered_column = {}
    #从前端拿到数据
    orderby_index = request.GET.get('_o')
    #如果有值，即有排序
    if orderby_index:
        orderby_key = admin_class.list_display[abs(int(orderby_index))]

        current_ordered_column[orderby_key] =orderby_index #为了让前端知道当前排序的列

        if orderby_index.startswith('-'):
            orderby_key = '-' + orderby_key

        return querysets.order_by(orderby_key),current_ordered_column

    else:
        return querysets,current_ordered_column


def get_serached_result(request,querysets,admin_class):
    """获取搜索条件内容，处理后返回搜索后的内容"""

    search_key = request.GET.get('_q')
    if search_key :
        q = Q()
        q.connector = 'OR'

        for search_field in admin_class.search_fields:
            #Q().children.append("字段名"，"字段内容"）：搜索
            q.children.append(("%s__contains"% search_field,search_key))# 在q添加子元素：search_field__contains=search_key


        return querysets.filter(q) #搜索过滤，留下选择的表中数据
    return querysets


@permissions.check_permission
@login_required
def table_obj_list(request,app_name,model_name):
    admin_class = site.enabled_admins[app_name][model_name]

    # 用于kingadmin下action行为所做操作
    if request.method == "POST":
        # print(request.POST)
        selected_action = request.POST.get('action')
        selected_ids = json.loads(request.POST.get('selected_ids'))
        # print(selected_action,selected_ids)
        if not selected_action:  # 如果有action参数,代表这是一个正常的action,如果没有,代表可能是一个删除动作
            if selected_ids:  # 这些选中的数据都要被删除
                admin_class.model.objects.filter(id__in=selected_ids).delete()
        else:  # 走action流程
            selected_objs = admin_class.model.objects.filter(id__in=selected_ids)

            admin_action_func = getattr(admin_class, selected_action)
            response = admin_action_func(request, selected_objs)
            # response = admin_action_func(request,selected_objs)
            if response:
                return response

    querysets = admin_class.model.objects.all().order_by('-id')

    # 1、过滤
    querysets,filter_condtions = get_filter_result(request,querysets)
    admin_class.filter_condtions = filter_condtions

    # 2、 搜索
    querysets = get_serached_result(request, querysets, admin_class)
    admin_class.search_key = request.GET.get('_q', '')

    # 3、排序
    querysets,sorted_column = get_orderby_result(request,querysets,admin_class)


    # 4、分页
    paginator = Paginator(querysets,admin_class.list_per_page)
    page = request.GET.get('_page')

    try:
        querysets = paginator.page(page)
    except PageNotAnInteger:
        # If page is not an integer, deliver first page.
        querysets = paginator.page(1)
    except EmptyPage:
        # If page is out of range (e.g. 9999), deliver last page of results.
        querysets = paginator.page(paginator.num_pages)#paginator.num_pages：总页数，即返回最后一页



    return render(request,"kingadmin/table_obj_list.html",locals())







@permissions.check_permission
@login_required
def table_obj_change(request,app_name,model_name,obj_id):
    """信息修改操作（页面）"""
    admin_class = site.enabled_admins[app_name][model_name]
    model_form = form_handle.create_dynamic_model_form(admin_class)
    obj = admin_class.model.objects.get(id=obj_id)
    if request.method == 'GET':
        # GET：查看当前页，返回当前对象的所有数据
        form_obj = model_form(instance=obj)
    else:
        # POST： 修改当前页，获取数据并保存新数据
        form_obj = model_form(instance=obj, data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect("/kingadmin/%s/%s/" % (app_name, model_name))
    # print("type--------------",type(form_obj))
    return render(request, 'kingadmin/table_obj_change.html', locals())


@permissions.check_permission
@login_required
def table_obj_add(request,app_name,model_name):
    """增加操作（页面）"""
    admin_class = site.enabled_admins[app_name][model_name]
    model_form = form_handle.create_dynamic_model_form(admin_class,form_add=True)
    if request.method == 'GET':
        # GET：查看当前页，返回当前对象的所有数据
        form_obj = model_form()
    else:
        # POST： 修改当前页，获取数据并保存新数据
        form_obj = model_form(data=request.POST)
        if form_obj.is_valid():
            form_obj.save()
            return redirect("/kingadmin/%s/%s/" % (app_name, model_name))

    return render(request, 'kingadmin/table_obj_add.html', locals())




@permissions.check_permission
@login_required
def table_obj_delete(request,app_name,model_name,obj_id):
    """删除操作"""
    admin_class = site.enabled_admins[app_name][model_name]
    obj = admin_class.model.objects.get(id=obj_id)
    status_action = 0 #用于html页面对是否为批量删除的判断，status_action=1：为批量删除，否则为单个删除
    if request.method == "POST":
        obj.delete()
        return redirect("/kingadmin/{app_name}/{model_name}/".format(app_name=app_name,model_name=model_name))
    return render(request,'kingadmin/table_obj_delete.html',locals())







@permissions.check_permission
@login_required
def crm_index(request,app_name):
    """kingadmin下的crm页面"""
    crm_list = []
    for app_name1,model_names in site.enabled_admins.items():
        if app_name1 == app_name:
            for model_name in model_names:
                crm_list.append(model_name)


    return render(request, 'kingadmin/crm_index.html', locals())