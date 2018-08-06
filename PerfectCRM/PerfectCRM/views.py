from django.shortcuts import render,redirect
from django.contrib.auth import authenticate,logout,login


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
            return redirect(request.GET.get("next","/crm/"))
        else:
            error_msg = "Wrong username or password!"
    return render(request,"login.html",{"error_msg":error_msg})


def acc_logout(request):
    logout(request)
    return redirect("/login/")