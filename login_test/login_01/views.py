from django.shortcuts import render,redirect,HttpResponse
from login_01 import forms,models
import hashlib

# Create your views here.
def index(request):
    pass
    return render(request,"index.html")

def login(request):
    if request.session.get('is_login', None):
        return redirect('/index/')


    err_msg = ''
    user_form = forms.UserForm()

    if request.method == "POST":
        user_form = forms.UserForm(request.POST)
        if user_form.is_valid():
            # 通过时设置session

            name = user_form.cleaned_data['name']
            password = user_form.cleaned_data['password']
            try:
                user_obj = models.User.objects.get(name=name)
                if user_obj.password == password:
                    request.session['is_login'] = True
                    request.session['user_id'] = user_obj.id
                    request.session['user_name'] = user_obj.name
                    return redirect('/index/')
            except:
                pass
        else:
            err_msg = "输入错误，请重新输入 ！"

            user_form = forms.UserForm(request.POST)
            return render(request, 'login.html', locals())


    return render(request,"login.html",locals())



def logout(request):
    if not request.session.get('is_login', None):
        # 如果本来就未登录，也就没有登出一说
        return redirect("/index/")
    request.session.flush()
    # 或者使用下面的方法
    # del request.session['is_login']
    # del request.session['user_id']
    # del request.session['user_name']
    return redirect("/login/")



def register(request):
    if request.session.get('is_login', None):
        # 登录状态不允许注册。你可以修改这条原则！
        return redirect("/index/")
    if request.method == "POST":
        register_form = forms.RegisterForm(request.POST)
        message = ""

        if register_form.is_valid():  # 获取数据

            username = register_form.cleaned_data['username']
            password1 = register_form.cleaned_data['password1']
            password2 = register_form.cleaned_data['password2']
            email = register_form.cleaned_data['email']
            if password1 != password2:  # 判断两次密码是否相同
                print("pwd")
                message = "两次输入的密码不同！"
                return render(request, 'register.html', locals())
            else:
                same_name_user = models.User.objects.filter(name=username)
                if same_name_user:  # 用户名唯一
                    print("same name")
                    message = '用户已经存在，请重新选择用户名！'
                    return render(request, 'register.html', locals())
                same_email_user = models.User.objects.filter(email=email)
                if same_email_user:  # 邮箱地址唯一
                    print("same email")
                    message = '该邮箱地址已被注册，请使用别的邮箱！'
                    return render(request, 'register.html', locals())

                # 当一切都OK的情况下，创建新用户

                new_user = models.User.objects.create()
                new_user.name = username
                new_user.password = password1
                new_user.email = email
                new_user.save()

                return redirect('/login/')
    register_form = forms.RegisterForm()
    return render(request, 'register.html', locals())


"""
def hash_code(s, salt='mysite_login'):
    h = hashlib.sha256()
    s += salt
    h.update(s.encode())  # update方法只接收bytes类型
    return h.hexdigest()
"""




def test_login(request):


    return render(request,"test_login.html")


def check_code(request):
    import io
    from login_01 import check_code

    mstream = io.BytesIO()
    img, code = check_code.create_validate_code()
    img.save(mstream, "GIF")
    # self.session["CheckCode"] = code
    print(code)
    return HttpResponse(mstream.getvalue())
