
from django.forms import ModelForm
from django import forms
from crm import models




class EnrollmentForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        # print("__new__",cls,args,kwargs)
        for field_name in cls.base_fields:# 获取表单中每个名
            filed_obj = cls.base_fields[field_name] # 获取表单中每个名称对应的字段对象
            filed_obj.widget.attrs.update({'class':'form-control'})
            if field_name in cls.Meta.readonly_fields:
                filed_obj.widget.attrs.update({'disabled': 'true'})
        return  ModelForm.__new__(cls)

    class Meta:
        model = models.StudentEnrollment
        #fields = ['name','consultant','status']
        fields = "__all__"
        exclude = ['contract_approved_date','contract_approved','contract_agreed','consultant','customer'] # 不显示该字段内容
        readonly_fields = [] # 只读字段

    def clean(self):
        """ 自定义方法 """
        # print("cleaned_dtat:",self.cleaned_data)

        if self.errors:
            raise forms.ValidationError(("Please fix errors before re-submit."))#如果错误，raise全局错误
        if self.instance.id is not None :#当前对象不为空，有值
            for field in self.Meta.readonly_fields:# 只读字段不允许修改，避免前端恶意修改数据，需拿数据库原数据与前端提交数据做对比，不一样则报错
                old_field_val = getattr(self.instance,field) #数据库里的数据
                form_val = self.cleaned_data.get(field) # 前端新接收数据
                print("filed differ compare:",old_field_val,form_val)
                if old_field_val != form_val: #数据不一样则在该字段报错
                    self.add_error(field,"Readonly Field: field should be '{value}' ,not '{new_value}' ".\
                                         format(**{'value':old_field_val,'new_value':form_val}))



class CustomerForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        # print("__new__",cls,args,kwargs)
        for field_name in cls.base_fields:
            filed_obj = cls.base_fields[field_name]
            filed_obj.widget.attrs.update({'class':'form-control'})

            if field_name in cls.Meta.readonly_fields:
                filed_obj.widget.attrs.update({'disabled': 'true'})
                #print("--new meta:",cls.Meta)

        #print(cls.Meta.exclude)
        return  ModelForm.__new__(cls)

    class Meta:
        model = models.CustomerInfo
        #fields = ['name','consultant','status']
        fields = "__all__"
        exclude = ['consult_content','status','consult_courses']
        readonly_fields = ['contact_type','contact','consultant','referral_from','source']


    def clean(self):
        '''form defautl clean method'''
        # print("\033[41;1mrun form defautl clean method...\033[0m",dir(self))
        # print(self.Meta.admin.readonly_fields)
        # print("cleaned_dtat:",self.cleaned_data)

        if self.errors:           #表单级别的错误
            raise forms.ValidationError(("Please fix errors before re-submit."))
        if self.instance.id is not None :#means this is a change form ,should check the readonly fields
            for field in self.Meta.readonly_fields:
                old_field_val = getattr(self.instance,field) #数据库里的数据
                form_val = self.cleaned_data.get(field)
                print("filed differ compare:",old_field_val,form_val)
                if old_field_val != form_val:
                    self.add_error(field,"Readonly Field: field should be '{value}' ,not '{new_value}' ".\
                                         format(**{'value':old_field_val,'new_value':form_val}))



class PaymentRecordForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        # print("__new__",cls,args,kwargs)
        for field_name in cls.base_fields:# 获取表单中每个名
            filed_obj = cls.base_fields[field_name] # 获取表单中每个名称对应的字段对象
            filed_obj.widget.attrs.update({'class':'form-control'})
            if field_name in cls.Meta.readonly_fields:
                filed_obj.widget.attrs.update({'disabled': 'true'})
        return  ModelForm.__new__(cls)

    class Meta:
        model = models.PaymentRecord
        #fields = ['name','consultant','status']
        fields = "__all__"
        exclude = ['enrollment','consultant'] # 不显示该字段内容
        readonly_fields = [] # 只读字段

    def clean(self):
        """ 自定义方法 """
        # print("cleaned_dtat:",self.cleaned_data)

        if self.errors:
            raise forms.ValidationError(("Please fix errors before re-submit."))#如果错误，raise全局错误
        if self.instance.id is not None :#当前对象不为空，有值
            for field in self.Meta.readonly_fields:# 只读字段不允许修改，避免前端恶意修改数据，需拿数据库原数据与前端提交数据做对比，不一样则报错
                old_field_val = getattr(self.instance,field) #数据库里的数据
                form_val = self.cleaned_data.get(field) # 前端新接收数据
                print("filed differ compare:",old_field_val,form_val)
                if old_field_val != form_val: #数据不一样则在该字段报错
                    self.add_error(field,"Readonly Field: field should be '{value}' ,not '{new_value}' ".\
                                         format(**{'value':old_field_val,'new_value':form_val}))





class CourseRecordForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        # print("__new__",cls,args,kwargs)
        for field_name in cls.base_fields:
            filed_obj = cls.base_fields[field_name]
            # if filed_obj.widget.attrs('type'):
            #     print("123")
            filed_obj.widget.attrs.update({'class':'form-control'})

            if field_name in cls.Meta.readonly_fields:
                filed_obj.widget.attrs.update({'disabled': 'true'})
                #print("--new meta:",cls.Meta)

        #print(cls.Meta.exclude)
        return  ModelForm.__new__(cls)

    class Meta:
        model = models.CourseRecord
        #fields = ['name','consultant','status']
        fields = "__all__"
        # exclude = []
        readonly_fields = []


    def clean(self):
        '''form defautl clean method'''
        # print("\033[41;1mrun form defautl clean method...\033[0m",dir(self))
        # print(self.Meta.admin.readonly_fields)
        # print("cleaned_dtat:",self.cleaned_data)

        if self.errors:           #表单级别的错误
            raise forms.ValidationError(("Please fix errors before re-submit."))
        if self.instance.id is not None :#用于新增数据，前端恶意修改只读字段，则做如下处理
            for field in self.Meta.readonly_fields:
                old_field_val = getattr(self.instance,field) #数据库里的数据
                form_val = self.cleaned_data.get(field)
                print("filed differ compare:",old_field_val,form_val)
                if old_field_val != form_val:
                    self.add_error(field,"Readonly Field: field should be '{value}' ,not '{new_value}' ".\
                                         format(**{'value':old_field_val,'new_value':form_val}))




class StudyRecordForm(ModelForm):
    def __new__(cls, *args, **kwargs):
        # print("__new__",cls,args,kwargs)
        for field_name in cls.base_fields:
            filed_obj = cls.base_fields[field_name]
            # if filed_obj.widget.attrs('type'):
            #     print("123")
            filed_obj.widget.attrs.update({'class':'form-control'})

            if field_name in cls.Meta.readonly_fields:
                filed_obj.widget.attrs.update({'disabled': 'true'})
                #print("--new meta:",cls.Meta)

        #print(cls.Meta.exclude)
        return  ModelForm.__new__(cls)

    class Meta:
        model = models.StudyRecord
        #fields = ['name','consultant','status']
        fields = "__all__"
        # exclude = []
        readonly_fields = []


    def clean(self):#用于新增数据，前端恶意修改只读字段，则做如下处理
        '''form defautl clean method'''
        # print("\033[41;1mrun form defautl clean method...\033[0m",dir(self))
        # print(self.Meta.admin.readonly_fields)
        # print("cleaned_dtat:",self.cleaned_data)

        if self.errors:           #表单级别的错误
            raise forms.ValidationError(("Please fix errors before re-submit."))
        if self.instance.id is not None :
            for field in self.Meta.readonly_fields:
                old_field_val = getattr(self.instance,field) #数据库里的数据
                form_val = self.cleaned_data.get(field)
                print("filed differ compare:",old_field_val,form_val)
                if old_field_val != form_val:
                    self.add_error(field,"Readonly Field: field should be '{value}' ,not '{new_value}' ".\
                                         format(**{'value':old_field_val,'new_value':form_val}))

