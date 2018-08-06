from django import forms
from login_01 import models
from captcha.fields import CaptchaField

class UserForm(forms.ModelForm):
    """与models中的user表有关,需有clean(self)自定义方法，否则is_valid为false"""
    name = forms.CharField(label='用户名')
    password = forms.CharField(label='密码' ,widget=forms.PasswordInput(attrs=({'type':'password'})))
    email = forms.EmailField(label='邮箱')
    captcha = CaptchaField(label='验证码')

    def __new__(cls, *args, **kwargs):
        # print("__new__",cls,args,kwargs)
        for field_name in cls.base_fields:
            filed_obj = cls.base_fields[field_name]
            filed_obj.widget.attrs.update({'class':'form-control'})


        #print(cls.Meta.exclude)
        return forms.ModelForm.__new__(cls)

    class Meta:
        model = models.User
        #fields = ['name','consultant','status']
        fields = "__all__"
        # exclude = ['consult_content','status','consult_courses']
        # readonly_fields = ['contact_type','contact','consultant','referral_from','source']


    def clean(self):
        #对整个表单进行校验
        '''form defautl clean method'''
        # print("\033[41;1mrun form defautl clean method...\033[0m",dir(self))
        # print(self.Meta.admin.readonly_fields)
        # print("cleaned_data:",self.cleaned_data)





class RegisterForm(forms.Form):
    """form 中的Form类"""
    username = forms.CharField(label="用户名", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    password1 = forms.CharField(label="密码", max_length=256, widget=forms.PasswordInput(attrs={'type':'password','class': 'form-control'}))
    password2 = forms.CharField(label="确认密码", max_length=256, widget=forms.PasswordInput(attrs={'type':'password','class': 'form-control'}))
    email = forms.EmailField(label="邮箱地址", widget=forms.EmailInput(attrs={'class': 'form-control'}))
    captcha = CaptchaField(label='验证码')

